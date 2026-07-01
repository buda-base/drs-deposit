import logging
import os
from pathlib import Path

import const as c
import pendulum
from drs_pds_transcode import transcode_volume
from project_manager_utils import (
    _get_drs3_step_name,
    get_next_work_pm_for_step,
    get_pms_for_step,
    pmItem,
    update_database_from_pm_items,
)
from s3pathlib import S3Path

logger = logging.getLogger(__name__)

DRS3_STAGE_STEP = _get_drs3_step_name(c.STAGE_STEP_NAME)
DRS3_TRANSCODE_STEP = _get_drs3_step_name(c.TRANSCODE_STEP_NAME)


def create_metadata_file(content_path: Path, metadata_file_path: Path):
    """
    Create a metadata file based on the content at the given path.

    :param content_path: Path to the file whose metadata will be used to generate the metadata file.
    :type content_path: Path
    :param metadata_file_path: Path where the generated metadata file will be saved.
    :type metadata_file_path: Path
    """
    logger.info(f"Generating metadata from {str(content_path)} into {str(metadata_file_path)}.")


def transcode_staged_volumes(work_staging_root: str) -> None:
    """
    Transcode all staged volumes for the given work.
    Like the staging process, it  uses what's on disk. So if a stage failed, it will
    not appear on disk.
    """
    work_pm: pmItem = get_next_work_pm_for_step(
        project_step=DRS3_TRANSCODE_STEP,
        prerquisite_step=DRS3_STAGE_STEP)
    if not work_pm:
        logger.info("No work found ready for transcoding.")
        return
    work_pms_item: pmItem
    staged_volume_pms_items: list[pmItem] = []
    work_pms_item, staged_volume_pms_items = get_pms_for_step(
        work_pm,
        staging_root,DRS3_TRANSCODE_STEP
    )
    
    work_pms_item.extras[c.PROJECT_STEP_RESULT_CODE_KEY] = 0        
    work_pms_item.extras[c.PROJECT_STEP_START_TIME_KEY] = pendulum.now("UTC")
    
    all_worked_ok: bool = True
    for staged_volume in staged_volume_pms_items:

        #
        # Make sure the pm_volume is staged - not all are, and we let them go. We can tell if there is a
        # p_m_s "transcode" for this pm (it was created just above)

        try:
            staged_volume.extras[c.PROJECT_STEP_RESULT_CODE_KEY] = 0
            staged_volume.extras[c.PROJECT_STEP_START_TIME_KEY] = pendulum.now("UTC")
            work_root = Path(staging_root,work_pm.label)
            volume_root = c.get_work_image_path(work_root) / staged_volume.label
            output_root = c.get_work_transcode_path(work_root) / staged_volume.label
            os.makedirs(output_root, exist_ok=True)
            logger.info(f"Transcoding volume {staged_volume.label} from {str(volume_root)} to {str(output_root)}")
            transcode_volume(volume_root, output_root)
            step_rc = 0
        except Exception as e:
            logger.error(f"Error transcoding volume {staged_volume.label}: {str(e)}")
            step_rc = 1
            all_worked_ok = False
        finally:
            staged_volume.extras[c.PROJECT_STEP_END_TIME_KEY] = pendulum.now("UTC")
            staged_volume.extras[c.PROJECT_STEP_RESULT_CODE_KEY] = step_rc
    
    work_pms_item.extras[c.PROJECT_STEP_END_TIME_KEY] = pendulum.now("UTC")
    work_pms_item.extras[c.PROJECT_STEP_RESULT_CODE_KEY] = 0 if all_worked_ok else 1

    update_database_from_pm_items(work_pms_item, staged_volume_pms_items)

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
#    work_pm: ProjectMembers = su.stage_next_work('/Users/jkatz/tmp/DRS3/Archive', '/Users/jkatz/tmp/DRS3/staging')
    transcode_staged_volumes('/Users/jkatz/tmp/DRS3/staging')