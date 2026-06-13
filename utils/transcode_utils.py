import logging
import os
from pathlib import Path
from typing import Any

import pendulum
import staging_utils as su
from BdrcDbLib.DrsContext import DrsDbContext
from BdrcDbModels.models import Works
from BdrcDbModels.project_manager import MemberTypes, ProjectMembers, ProjectMemberSteps, Steps
from BdrcDbModels.SqlAlchemy_get_or_create import get_or_create
from drs_pds_transcode import transcode_volume
from s3pathlib import S3Path
from sqlalchemy import select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _get_drs3_step_name(step_name: str) -> Steps:
    """
    Pre-fetch some standard lookup model objects
    """
    with DrsDbContext(su.MY_DB) as db:
        session: Session = db.get_session()
        transcode_step = select(Steps).where(Steps.s_name == step_name)  # pyright: ignore[reportArgumentType]
        transcode_step = session.execute(transcode_step).scalar_one_or_none()
        if not transcode_step:
            raise RuntimeError(f"{step_name} step not found")
        return transcode_step


TRANSCODE_NAME = "transcode"
DRS3_STEP_TRANSCODE = _get_drs3_step_name(TRANSCODE_NAME)


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


def transcode_staged_volumes(work_pm: Any):
    """Transcode all staged volumes for the given work."""

    # If this is not a ProjectMembers object representing a work
    if not isinstance(work_pm, ProjectMembers) or not work_pm.work:
        raise TypeError("work_pm must be a ProjectMembers model object")

    work_id = work_pm.work.workId
    if work_id is None:
        return None
    staging_root = os.path.expanduser(su.STAGING_ROOT)

    work_transcode_pms: ProjectMemberSteps = None

    any_failed: bool = False
    # Open context to get work and create PMS records, then close before transcode
    with DrsDbContext("qa") as db:
        session = db.get_session()

        work_transcode_pms, is_new = get_or_create(
            session,
            ProjectMemberSteps,
            project_member=work_pm,
            project_step=DRS3_STEP_TRANSCODE)
        work_transcode_pms.project_step_start_time = pendulum.now("UTC")
        session.commit()
        pm_volumes: list[ProjectMembers] = []

        volume_member_type: MemberTypes = session.execute(select(MemberTypes)
        .where(MemberTypes.m_type == "volume")).scalar_one_or_none()  # pyright: ignore[reportArgumentType]
        
        if not volume_member_type:
            raise RuntimeError("Volume member type not found")

        # Get project members of type "volume" whose related volume belongs to this work.abs
        # The "has(...) clause is necessary because we are going through a relationship, not a direct test
        # as in the first condition.
        get_pms_for_work = select(ProjectMembers).where(
            ProjectMembers.pm_type == volume_member_type,
            ProjectMembers.volume.has(work=work_pm.work)
        )
        pm_volumes = session.execute(get_pms_for_work).scalars().all()


        # add volumes that have never been staged to the list of volumes to state.
        for pm_volume in pm_volumes:
            # If there are no staged project member steps for this volume, skip it.abs
            # We cant transcode until it's staged.
            if not any(s.step == "staged" and s.result_code == 0 for s in pm_volume.project_member_steps):
                continue
            vol_transcode_step_pms, is_new = get_or_create(
                session,
                ProjectMemberSteps,
                project_member=pm_volume,
                project_step=DRS3_STEP_TRANSCODE
            )
            vol_transcode_step_pms.project_step_start_time = pendulum.now("UTC" )
            session.flush()
        session.commit()

    # Now, outside DB context, run transcode for each volume
    for pm_volume in pm_volumes:
        #
        # Make sure the pm_volume is staged - not all are, and we let them go. We can tell if there is a
        # p_m_s "transcode" for this pm (it was created just above)
        this_failed: bool = False
        try:
            _work: Works  = pm_volume.volume.work 
            work_root = Path(staging_root, _work.WorkName)
            volume_root = Path(work_root, 'images', pm_volume.volume.label) 
            output_root = work_root / 'drs' / pm_volume.volume.label
            logger.info(f"Transcoding volume {pm_volume.volume.label} from {str(volume_root)} to {str(output_root)}")
            transcode_volume(volume_root, output_root)
        except Exception as e:
            logger.error(f"Error transcoding volume {pm_volume.volume.label}: {str(e)}")
            this_failed = True
            any_failed = True
        finally:
            # Reopen context to update PMS for this volume
            with DrsDbContext("qa") as db2:
                session2 = db2.get_session()

                pms_transcode_step = [s for s in pm_volume.project_member_steps if s.step == DRS3_STEP_TRANSCODE]
                if len(pms_transcode_step) != 1:
                    errstr = (
                        f"{len(pms_transcode_step)} transcode steps found for volume " 
                        f"{pm_volume.volume.label}"
                    )
                    raise RuntimeError(errstr)

                vol_transcode_step_pms = pms_transcode_step[0]
                vol_transcode_step_pms.end_time = pendulum.now("UTC")
                vol_transcode_step_pms.result_code = 0 if not this_failed else 1
                session2.merge(vol_transcode_step_pms)
                session2.commit()


    # Reopen context to update PMS for work
    with DrsDbContext("qa") as db3:
        session3 = db3.get_session()
        #
        # Create a projectMember
        # If null, should abort here.
        work_transcode_pms.end_time=pendulum.utcnow(),
        work_transcode_pms.project_step_result_code=0 if not any_failed else 1
        session3.merge(work_transcode_pms)
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


if __name__ == "__main__":
    import staging_utils as su
    work_pm: ProjectMembers = su.stage_next_work('/Users/jkatz/tmp/DRS3/Archive', '/Users/jkatz/tmp/DRS3/staging')
    transcode_staged_volumes(work_pm)