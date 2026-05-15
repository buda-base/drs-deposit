"""
DAG to process staged entries: transcode, generate metadata, and upload to S3, as specified in Architecture.md.
"""
import os
from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import pendulum
from pathlib import Path
import BdrcDbModels.project_manager as pm
from BdrcDbLib.DrsContext import DrsDbContext
from dags.drs_utils import create_metadata_file, send_to_s3
from dags.drs_pds_transcode import transcode

STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "~/tmp/DRS3/staging")

with DAG(
    dag_id='drs3_process_staged',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
) as dag:

    @task
    def get_next_staged_work():
        """Find the next staged work that hasn't been transcoded."""
        with DrsDbContext('qa') as db:
            session = db.get_session()
            work = session.query(pm.ProjectMembers).join(pm.ProjectMemberSteps).filter(
                pm.ProjectMembers.member_type=='work',
                pm.ProjectMemberSteps.step=='staged',
                ~pm.ProjectMembers.projectmembersteps.any(pm.ProjectMemberSteps.step=='transcode')
            ).order_by(pm.ProjectMemberSteps.start_time).first()
            if not work:
                return None
            return work.id

    @task
    def transcode_staged_volumes(work_id: int):
        """Transcode all staged volumes for the given work."""
        if work_id is None:
            return None
        staging_root = os.path.expanduser(STAGING_ROOT)
        # Open context to get work and create PMS records, then close before transcode
        with DrsDbContext('qa') as db:
            session = db.get_session()
            work = session.query(pm.ProjectMembers).get(work_id)
            if not work:
                return None
            # Mark PMS with transcode step for work
            pms = pm.ProjectMemberSteps(
                projectmember_id=work.id,
                step='transcode',
                start_time=datetime.utcnow()
            )
            session.add(pms)
            session.flush()
            volume_ids = []
            for volume in work.volumes:
                if not any(s.step=='staged' and s.result_code==0 for s in volume.projectmembersteps):
                    continue
                pms_vol = pm.ProjectMemberSteps(
                    projectmember_id=volume.id,
                    step='transcode',
                    start_time=datetime.utcnow()
                )
                session.add(pms_vol)
                session.flush()
                volume_ids.append((volume.id, pms_vol.id))
            session.commit()
            work_name = work.work_name
        # Now, outside DB context, run transcode for each volume
        for volume_id, pms_vol_id in volume_ids:
            transcode(Path(staging_root), work_name)
            # Reopen context to update PMS for this volume
            with DrsDbContext('qa') as db2:
                session2 = db2.get_session()
                pms_vol = session2.query(pm.ProjectMemberSteps).get(pms_vol_id)
                pms_vol.end_time = datetime.utcnow()
                pms_vol.result_code = 0
                session2.commit()
        # Reopen context to update PMS for work
        with DrsDbContext('qa') as db3:
            session3 = db3.get_session()
            pms = session3.query(pm.ProjectMemberSteps).filter_by(projectmember_id=work_id, step='transcode').order_by(pm.ProjectMemberSteps.start_time.desc()).first()
            if pms:
                pms.end_time = datetime.utcnow()
                pms.result_code = 0
                session3.commit()
        return work_id

    @task
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

    @task
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