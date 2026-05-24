"""
DAG to process staged entries: transcode, generate metadata, and upload to S3, as specified in Architecture.md.
"""
import os
from airflow import DAG

from datetime import datetime
import pendulum

from utils.drs_utils import create_metadata_file, send_to_s3
from dags.drs_pds_transcode import transcode
import utils.staging_utils as su
import utils.drs_utils as du


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
    def transcode_staged_volumes(work_id: int):
        return du.transcode_staged_volumes(work_id)

 

    @dag.task
    def generate_metadata(work_id: int):
        """Generate metadata for the given work."""
        if work_id is None:
            return None
        staging_root = os.path.expanduser(STAGING_ROOT)
        with DrsDbContext('qa') as db:
            session = db.get_session()
            work = session.query(pm.ProjectMembers).get(work_id)
            if not work:
                return None
            metadata_path = Path(staging_root) / f"{work.work_name}_metadata.json"
            create_metadata_file(Path(staging_root) / work.work_name, metadata_path)
        return work_id

    @dag.task
    def upload_to_s3(work_id: int):
        """Upload the work and its metadata to S3."""
        if work_id is None:
            return 'No work to upload.'
        staging_root = os.path.expanduser(STAGING_ROOT)
        # Open context to get work and metadata path, then close before upload
        with DrsDbContext('qa') as db:
            session = db.get_session()
            work = session.query(pm.ProjectMembers).get(work_id)
            if not work:
                return 'Work not found.'
            work_name = work.work_name
            metadata_path = Path(staging_root) / f"{work.work_name}_metadata.json"
        # Outside DB context, do the upload
        upload_success = True
        try:
            send_to_s3(Path(staging_root) / work_name, None)  # S3Path to be set
            send_to_s3(metadata_path, None)
        except Exception:
            upload_success = False
        # Reopen context to update PMS
        with DrsDbContext('qa') as db2:
            session2 = db2.get_session()
            work = session2.query(pm.ProjectMembers).get(work_id)
            for obj in [*work.projectmembersteps]:
                if obj.step in ('transcode', 'upload') and not obj.end_time:
                    obj.end_time = datetime.utcnow()
                    obj.result_code = 0 if upload_success else 1
            session2.commit()
        return 'Upload complete.'

    wid = get_next_staged_work()
    transcoded = transcode_staged_volumes(wid)
    metadata = generate_metadata(transcoded)
    upload_to_s3(metadata)