"""
DAG to process staged entries: transcode, generate metadata, and upload to S3, as specified in Architecture.md.
"""
import os
from pathlib import Path
from typing import Any

import pendulum
from airflow import DAG
from airflow.exceptions import AirflowFailException

import utils.staging_utils as su
import utils.transcode_utils as tu

with DAG(
    dag_id='drs3_process_staged',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
) as dag:

    @dag.task
    def get_next_staged_work():
        return su.get_next_unstaged_work()

    @dag.task
    def transcode_staged_volumes(work_ : Any):
        return tu.transcode_staged_volumes(work_)

 

    @dag.task
    def generate_metadata(work: Any):
        """Generate metadata for the given work."""
        if work is None:
            raise AirflowFailException("No work to generate metadata for.")
        staging_root = su.STAGING_ROOT
        tu.create_metadata_file(Path(staging_root), work)
        return work

    @dag.task
    def upload_to_s3(work: Any):
        """Upload the work and its metadata to S3."""
        if work is None:
            raise AirflowFailException("No work to upload.")
        staging_root = os.path.expanduser(su.STAGING_ROOT)
        try:
            tu.send_to_s3(Path(staging_root), work)  # S3Path to be set
        except Exception as err:
            raise AirflowFailException("Failed to upload to DRS.") from err


    work_ = get_next_staged_work()
    transcoded = transcode_staged_volumes(work_)
    metadata = generate_metadata(transcoded)
    upload_to_s3(metadata)