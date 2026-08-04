# pyright: reportArgumentType=false

"""
DAG to process staged entries: transcode, generate metadata, and upload to S3, as specified in Architecture.md.
"""
import logging
import os
from pathlib import Path

import project_manager_utils as pmu
import transcode_utils as tu
from airflow import DAG
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import get_current_context, task
from airflow.sdk.exceptions import AirflowFailException

logger = logging.getLogger(__name__)

DRS3_PROCESS_STAGED_DAG_ID: str ='drs3_process_staged'

STAGING_ROOT = os.environ["DRS3_STAGING_ROOT"]
LIMIT_WORKS_TO_PROCESS = int(os.environ.get("DRS3_LIMIT_WORKS_TO_PROCESS", 1))
MAX_ACTIVE_RUNS = int(os.environ.get("DRS3_PROCESS_MAX_ACTIVE_RUNS", 4))

with DAG(
    dag_id='drs3_process_launcher',
    schedule="*/30 * * * *",
    catchup=False,
): 
    @task
    def get_works_to_process(limit: int = 1) -> list[pmu.pmItem]:
        work_list: list[pmu.pmItem] = tu.get_works_to_transcode(limit)
        return work_list

    @task
    def build_stage_work_run_confs(work_names: list[pmu.pmItem]) -> list[dict[str, str]]:

        run_confs = [{"work_name": work_name.label} for work_name in work_names]
        logger.info(
            "Emitting %d trigger events for %s (dag_id=%s)",
            len(run_confs),
            DRS3_PROCESS_STAGED_DAG_ID,
            dag.dag_id,
        )
        return run_confs
 
    work_names = get_works_to_process(LIMIT_WORKS_TO_PROCESS)
    stage_work_run_confs = build_stage_work_run_confs(work_names) # type: ignore
 
     # partial sets shared args once; expand triggers one run per conf item.
     # Keep reset_dag_run=False so an existing run_id is not reset/rerun.
    TriggerDagRunOperator.partial(
        task_id="trigger_stage_work_dag_runs",
        trigger_dag_id=DRS3_PROCESS_STAGED_DAG_ID,
        wait_for_completion=False,
        reset_dag_run=False,
    ).expand(conf=stage_work_run_confs)


# This DAG is triggered manually from DAG 'drs3_process_launcher'
with DAG(
    dag_id=DRS3_PROCESS_STAGED_DAG_ID,
    # jimkatz: drs-deposit#126 - schedule and start_date are set in the launcher DAG, not here.
    # This breaks loading
    # drs-deposit#126 schedule='*/30 * * * *',
    # start_date = pendulum.datetime(2026, 7, 2, 0, 0, 0, tz="UTC"),
    catchup=False,
    tags=["drs3","transcode","metadata"],
    max_active_runs=MAX_ACTIVE_RUNS,
) as dag:

    @task
    def get_work_name_to_process():
        """
        Get the next staged work item that has not been transcoded yet
        """
        context = get_current_context()
        dag_run = context.get("dag_run")
        dag_run_conf = dag_run.conf if dag_run else {}
        if not dag_run_conf:
            raise AirflowFailException("No DAG run configuration provided.")
        work_name = dag_run_conf.get("work_name")  # pyright: ignore[reportOptionalMemberAccess]
        if not work_name:
            raise AirflowFailException("No work_name provided in DAG run configuration.")
        work_ = pmu.get_work_pm_from_name(work_name)
        if work_ is None:
            raise AirflowFailException(f"No work found for work_name={work_name}.")
        return work_

    @task
    def transcode_staged_volumes(work_: pmu.pmItem):
        out_work: pmu.pmItem
        try:
            out_work = tu.transcode_staged_volumes(STAGING_ROOT, work_)
        except Exception as e:
            raise AirflowFailException(f"Error transcoding work {work_.label}: {e}") from e
        return out_work

 

    @task
    def generate_metadata(work: pmu.pmItem):
        """Generate metadata for the given work."""

        import const as c

        if work is None:
            raise AirflowFailException("No work to generate metadata for.")
        work_staging_root: Path = Path(STAGING_ROOT, work.label)
        try:
            work_metadata_root: Path =  c.get_work_metadata_path(work_staging_root)
            tu.create_metadata_file(work_staging_root, work_metadata_root)
        except Exception as err:
            raise AirflowFailException("Failed to generate metadata.") from err
        return work

    @task
    def upload_to_s3(work: pmu.pmItem):
        """Upload the work and its metadata to S3."""
        if work is None or not work.label or not work.o_id:
            raise AirflowFailException(f"defective work Item {work.o_id=},{work.label=}.")
        work_staging_root = Path(STAGING_ROOT, work.label)
        try:
            tu.send_to_s3(work_staging_root, work)  # S3Path to be set
        except Exception as err:
            raise AirflowFailException("Failed to upload to DRS.") from err


    # Begin task flow
    # drs-deposit#126 - get the work list from the context like drs3_stage_works.stage_next_work_task

    work_name = get_work_name_to_process()
    transcoded = transcode_staged_volumes(work_name)
    metadata = generate_metadata(transcoded)
    # Sepaupload is separate DAG - we may be limited / throttled in how many we do. 
    # upload_to_s3(metadata)