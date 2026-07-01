"""
Producer DAG that checks candidate works file changes and emits a Dataset event.
"""

import logging
import os
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.sdk import Asset
from populate_members import populate_members

SRC_ROOT = os.environ.get("DRS3_ARCHIVE_ROOT", "/mnt/Archive")
STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "/mnt/staging")
DRS3_CANDIDATE_WORKS = Path(STAGING_ROOT, "drs3_candidate_works.lst")
DRS3_CANDIDATE_TMP_DIR = Path(STAGING_ROOT, "tmp")
DRS3_CANDIDATE_SNAPSHOT_PREFIX = ".tmp.drs3_candidate_works."
DRS3_CANDIDATE_SNAPSHOT_RETAIN_COUNT = 50
DRS3_CANDIDATE_ARCHIVE_ZIP = DRS3_CANDIDATE_TMP_DIR / "tmp.drs3_candidates.zip"
DRS3_STAGE_WORKS_ASSET = Asset("drs3://candidate_works/changed")


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
    schedule="0 * * * *",
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    tags=["staging", "works", "project_members", "drs3"],
) as dag:
    @task.short_circuit
    def populate_candidate_work_members() -> bool:
        """
        Get any new works from the list. The lnlist could be a new file, or an extension of the old file.
        There is no requirement to remove the old file.
        """
        if not DRS3_CANDIDATE_WORKS.exists():
            logger.info("No candidate works file found.")
            return False

        sorted_lines = _read_sorted_unique_lines(DRS3_CANDIDATE_WORKS)
        current_snapshot = _write_snapshot(sorted_lines)
        _archive_old_snapshots()

        previous_snapshot = _latest_previous_snapshot(current_snapshot)
        previous_lines = _read_sorted_unique_lines(previous_snapshot) if previous_snapshot else []
        new_work_names = _comm_new_lines(previous_lines, sorted_lines)

        if not new_work_names:
            return False

        populate_members(SRC_ROOT, new_work_names)
        return True

    @task(outlets=[DRS3_STAGE_WORKS_ASSET])
    def emit_stage_works_asset_event() -> str:
        return "candidate works changed"

    populate_candidate_work_members() >> emit_stage_works_asset_event()
