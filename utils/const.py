"""
constants
"""
import os
from pathlib import Path

DRS3_PROJECT_NAME: str = "DRS3"
DRS3_PROJECT_DESC: str = "DRS3 project"
STAGE_STEP_NAME: str = "stage"
TRANSCODE_STEP_NAME: str = "transcode"
UPLOAD_STEP_NAME: str = "upload"
PUBLISH_CONFIRM_STEP_NAME: str = "publish_confirm"
PROJECT_MEMBER_TYPE_WORK: str = "work"
PROJECT_MEMBER_TYPE_VOLUME: str = "volume"

# These must correspond to project_manager.ProjectMemberStep fields
PROJECT_STEP_START_TIME_KEY: str = "project_step_start_time"
PROJECT_STEP_RESULT_CODE_KEY: str = "project_step_result_code"
PROJECT_STEP_END_TIME_KEY: str = "project_step_end_time"

StrPath = str | os.PathLike[str]
def get_work_image_path(work_path: StrPath) -> Path:
    """
    Get the path to the images for a given work in the archive.
    :param work_path: path to the work directory
    :type work_path: StrPath
    :return: Path to the images directory for the given work
    :rtype: Path
    """
    return Path(work_path) / "images"

def get_work_transcode_path(work_path: StrPath) -> Path:
    """
    Get the path to the transcode output for a given work in the archive.
    :param work_path: path to the work directory
    :type work_path: StrPath
    :return: Path to the transcode output directory for the given work
    :rtype: Path
    """
    return Path(work_path) / "drs"

def get_work_metadata_path(work_path: StrPath) -> Path:
    """
    Get the path to the metadata output for a given work in the archive.
    :param work_path: path to the work directory
    :type work_path: StrPath
    :return: Path to the metadata output file for the given work
    :rtype: Path
    """
    return Path(work_path) / "metadata.json"