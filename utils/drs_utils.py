import logging
import os
from pathlib import Path

import pendulum
from  s3pathlib import S3Path
from pathlib import Path
from BdrcDbModels.project_manager import ProjectMembers, ProjectMemberSteps
from BdrcDbModels.models import Works, Volumes
from BdrcDbLib.DrsContext import DrsDbContext

STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "~/tmp/DRS3/staging")

logger = logging.getLogger(__name__)

def stage_content(source_path: Path, staging_path: Path):
    """
    Stub function to stage content from source_path to staging_path.

    :param source_path: Local path to the source file to be staged.
    :type source_path: Path
    :param staging_path: Local path where the staged file will be saved.
    :type staging_path: Path
    """
    logger.info(f"Staging content from {str(source_path)} to {str(staging_path)}.")
    
def create_metadata_file(content_path: Path, metadata_file_path: Path):
    """
    Create a metadata file based on the content at the given path.

    :param content_path: Path to the file whose metadata will be used to generate the metadata file.
    :type content_path: Path
    :param metadata_file_path: Path where the generated metadata file will be saved.
    :type metadata_file_path: Path
    """
    logger.info(f"Generating metadata from {str(content_path)} into {str(metadata_file_path)}.")
 
def transcode_staged_volumes(work_id: int):
    """Transcode all staged volumes for the given work."""
    if work_id is None:
        return None
    staging_root = os.path.expanduser(STAGING_ROOT)
    # Open context to get work and create PMS records, then close before transcode
    with DrsDbContext('qa') as db:
        session = db.get_session()
        work = session.query(Works).get(work_id)
        if not work:
            return None
        # Mark PMS with transcode step for work
        pms = ProjectMemberSteps(
            project_member_id=work.id,
            step='transcode',
            start_time=datetime.utcnow()
        )
        session.add(pms)
        session.flush()
        volume_ids = []
        for volume in work.volumes:
            if not any(s.step=='staged' and s.result_code==0 for s in volume.projectmembersteps):
                continue
            pms_vol = ProjectMemberSteps(
                project_member_id=volume.id,
                step_id =                step='transcode',
                project_step_start_time=pendulum.now()
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
            pms_vol = session2.query(ProjectMemberSteps).get(pms_vol_id)
            pms_vol.end_time = pendulum.now("UTC")
            pms_vol.result_code = 0
            session2.commit()
    # Reopen context to update PMS for work
    with DrsDbContext('qa') as db3:
        session3 = db3.get_session()
        pms = session3.query(ProjectMemberSteps).filter_by(project_member_id=work_id, step='transcode').order_by(ProjectMemberSteps.project_step_start_time.desc()).first()
        if pms:
            pms.project_step_end_time = pendulum.now("UTC")
            pms.project_step_result_code = 0
            session3.commit()
    return work_id  

def send_to_s3(source_path: Path, destination_s3_path: S3Path):
    """
    Stub function to send a file from source_path to destination_s3_path (S3).

    :param source_path: Local path to the source file to be uploaded.
    :type source_path: Path
    :param destination_s3_path: S3Path object representing the destination path in S3.
    :type destination_s3_path: S3Path
    """
    logger.info(f"Sending {str(source_path)} to {str(destination_s3_path)} using s3pathlib.")


