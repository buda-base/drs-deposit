"""
Producer DAG that checks candidate works and triggers one stage DAG run per new work.
"""

import logging
import os
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import task
from populate_members import populate_members

SRC_ROOT = os.environ.get("DRS3_ARCHIVE_ROOT", "/mnt/Archive")
STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "/mnt/staging")
DRS3_CANDIDATE_WORKS = Path(STAGING_ROOT, "drs3_candidate_works.lst")
DRS3_CANDIDATE_TMP_DIR = Path(STAGING_ROOT, "tmp")
DRS3_CANDIDATE_SNAPSHOT_PREFIX = ".tmp.drs3_candidate_works."
DRS3_CANDIDATE_SNAPSHOT_RETAIN_COUNT = 50
DRS3_CANDIDATE_ARCHIVE_ZIP = DRS3_CANDIDATE_TMP_DIR / "tmp.drs3_candidates.zip"
DRS3_STAGE_WORKS_DAG_ID = "drs3_stage_works"


def _read_sorted_unique_lines(path: Path) -> list[str]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return sorted(set(lines))


def _write_snapshot(lines: list[str]) -> Path:
    DRS3_CANDIDATE_TMP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    snapshot = DRS3_CANDIDATE_TMP_DIR / f"{DRS3_CANDIDATE_SNAPSHOT_PREFIX}{ts}.lst"
    snapshot.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return snapshot


def _archive_old_snapshots() -> None:
    snapshots = sorted(
        DRS3_CANDIDATE_TMP_DIR.glob(f"{DRS3_CANDIDATE_SNAPSHOT_PREFIX}*.lst"),
        key=lambda p: p.name,
    )
    if len(snapshots) <= DRS3_CANDIDATE_SNAPSHOT_RETAIN_COUNT:
        return

    to_archive = snapshots[:-DRS3_CANDIDATE_SNAPSHOT_RETAIN_COUNT]
    with zipfile.ZipFile(DRS3_CANDIDATE_ARCHIVE_ZIP, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
        for snapshot in to_archive:
            zf.write(snapshot, arcname=snapshot.name)

    for snapshot in to_archive:
        snapshot.unlink(missing_ok=True)


def _latest_previous_snapshot(current_snapshot: Path) -> Path | None:
    snapshots = sorted(
        DRS3_CANDIDATE_TMP_DIR.glob(f"{DRS3_CANDIDATE_SNAPSHOT_PREFIX}*.lst"),
        key=lambda p: p.name,
    )
    for candidate in reversed(snapshots):
        if candidate != current_snapshot:
            return candidate
    return None


def _comm_new_lines(previous: list[str], current: list[str]) -> list[str]:
    previous_set = set(previous)
    return [line for line in current if line not in previous_set]

logger = logging.getLogger(__name__)
with DAG(
    dag_id="drs3_candidate_works_asset",
    schedule="*/15 * * * *",
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    tags=["staging", "works", "project_members", "drs3"],
) as dag:
    @task
    def populate_candidate_work_members() -> list[str]:
        """
        Get any new works from the list. The lnlist could be a new file, or an extension of the old file.
        There is no requirement to remove the old file.
        """
        if not DRS3_CANDIDATE_WORKS.exists():
            logger.info("No candidate works file found.")
            return []

        sorted_lines = _read_sorted_unique_lines(DRS3_CANDIDATE_WORKS)
        current_snapshot = _write_snapshot(sorted_lines)
        _archive_old_snapshots()

        previous_snapshot = _latest_previous_snapshot(current_snapshot)
        previous_lines = _read_sorted_unique_lines(previous_snapshot) if previous_snapshot else []
        new_work_names = _comm_new_lines(previous_lines, sorted_lines)

        if not new_work_names:
            return []

        populate_members(SRC_ROOT, new_work_names)
        return new_work_names

    @task
    def build_stage_work_run_confs(work_names: list[str]) -> list[dict[str, str]]:
        run_confs = [{"work_name": work_name} for work_name in work_names]
        logger.info(
            "Emitting %d trigger events for %s (dag_id=%s)",
            len(run_confs),
            DRS3_STAGE_WORKS_DAG_ID,
            dag.dag_id,
        )
        return run_confs

    work_names = populate_candidate_work_members()
    stage_work_run_confs = build_stage_work_run_confs(work_names) # type: ignore

    # partial sets shared args once; expand triggers one run per conf item.
    # Keep reset_dag_run=False so an existing run_id is not reset/rerun.
    TriggerDagRunOperator.partial(
        task_id="trigger_stage_work_dag_runs",
        trigger_dag_id=DRS3_STAGE_WORKS_DAG_ID,
        wait_for_completion=False,
        reset_dag_run=False,
    ).expand(conf=stage_work_run_confs)
