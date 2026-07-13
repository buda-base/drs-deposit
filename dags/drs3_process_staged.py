"""
DAG to process staged entries: transcode, generate metadata, and upload to S3, as specified in Architecture.md.
"""
import os
from pathlib import Path

import pendulum
import project_manager_utils as pmu
import transcode_utils as tu
from airflow import DAG
from airflow.sdk import task
from airflow.sdk.exceptions import AirflowFailException, AirflowSkipException

STAGING_ROOT = os.environ["DRS3_STAGING_ROOT"]

with DAG(
    dag_id='drs3_process_staged',
    schedule='*/30 * * * *',
    start_date = pendulum.datetime(2026, 7, 2, 0, 0, 0, tz="UTC"),
    catchup=False,
    tags=["drs3","transcode","metadata","upload"],
) as dag:

    @task
    def get_next_staged_work():
        """
        Get the next staged work item that has not been transcoded yet
        """
        _nsw = pmu.get_next_work_to_transcode()
        if not _nsw:
            raise AirflowSkipException("No staged work to process.")
        return _nsw
    @task
    def transcode_staged_volumes(work_ : pmu.pmItem):
        return tu.transcode_staged_volumes(STAGING_ROOT, work_)

 

    @task
    def generate_metadata(work: pmu.pmItem):
        """Generate metadata for the given work."""

        import const as c

        if work is None:
            raise AirflowFailException("No work to generate metadata for.")
        work_staging_root: Path = Path(STAGING_ROOT, work.label)
        work_metadata_root: Path =  c.get_work_metadata_path(work_staging_root)
        tu.create_metadata_file(work_staging_root, work_metadata_root)
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


    work_ = get_next_staged_work()
    transcoded = transcode_staged_volumes(work_)
    metadata = generate_metadata(transcoded)
    upload_to_s3(metadata)