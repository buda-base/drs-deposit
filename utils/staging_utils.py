# xxpyright: xxreportArgumentType=false
# avoid warning for TIMESTAMP mapped columns (e.g. ..start_time ) F401
"""
Supports DAG. Extracted for testing
"""


import logging
from pathlib import Path

import const as c
import pendulum
import project_manager_utils as pmu
from archive_ops.api import get_archive_location
from project_manager_utils import (
    get_next_work_pm_for_step,
    get_pms_for_step,
    get_work_pm_for_step,
    pmItem,
    update_database_from_pm_items,
)

logger = logging.getLogger(__name__)

def stage_next_work(source_root: str, staging_root: str, work_name: str | None = None) -> pmItem | None:
    """
    Finds the next unstaged work (or a requested work by name), creates the
    ProjectMemberSteps for the work and its volumes, and stages each volume.
    :param source_root: root directory for source content
    :param staging_root: root directory for staging
    :type source_root: str
    :type staging_root: str
    :param work_name: optional explicit work name to stage
    :type work_name: str | None
    :return: pmItem instance for the work being staged
    :rtype: pmItem

    ACHTUNG! the sources for staging are assumed to be in the archive in
    archive_ops.api.get_archive_location(...) format
    """
# Aloow calling without work name, and use the DB
# Unknwn: does this break the db based search? No.absWe used to be tagging 
# works that had PMs, but no steps.abs# With the
# new pattern of processing 'n' at a time, the PMS'abs
# are created when neeeded, not sought and filtered (looking for one iwth
# no data).)
    if work_name:
        work_to_stage_pm_item = get_work_pm_for_step(work_name, pmu.DRS3_STAGE_STEP)
    else:
        work_to_stage_pm_item = get_next_work_pm_for_step(pmu.DRS3_STAGE_STEP)

    if not work_to_stage_pm_item:
        return

    archive_source_root: Path = Path(get_archive_location(source_root, work_to_stage_pm_item.label))
    staging_source_work_root: Path = Path(staging_root, work_to_stage_pm_item.label)
    unstaged_work_pms_item: pmItem
    unstaged_volumes_pms_items: list[pmItem] 
    unstaged_work_pms_item, unstaged_volumes_pms_items = get_pms_for_step(
        work_to_stage_pm_item, archive_source_root, pmu.DRS3_STAGE_STEP
    )
    if not unstaged_volumes_pms_items:
        raise RuntimeError(
            f"No volumes to stage for work {work_to_stage_pm_item.label} "
            f"(id={work_to_stage_pm_item.o_id})"
        )
    try:
        do_staging(unstaged_work_pms_item, unstaged_volumes_pms_items, archive_source_root, staging_source_work_root)
    except Exception as e:
        logger.error(f"- X staging work {work_to_stage_pm_item.label} (id={work_to_stage_pm_item.o_id}): {e}")

        # Maybe partial success
        unstaged_work_pms_item.extras["project_step_result_code"] = 1
    finally:        
        update_database_from_pm_items(unstaged_work_pms_item, unstaged_volumes_pms_items)
        if unstaged_work_pms_item.extras.get("project_step_result_code", -1) != 0:
            logger.error(f"- X staging work {unstaged_work_pms_item.label} (id={unstaged_work_pms_item.o_id})")
        else:
            logger.info(f"+ Staged work {unstaged_work_pms_item.label} (id={unstaged_work_pms_item.o_id})")

    return unstaged_work_pms_item

def do_staging(
    work_pms_item: pmItem,
    volumes_pms_items: list[pmItem],
    work_source_root: Path, staging_root: Path) -> pmItem:
    """
    Stage mainline
    :param work_pms_item: the pmItem for the work being staged, updated out of context
    :param volumes_pms_items: list of pmItem for the volumes being staged, updated out of context
    :param work_source_root: root directory for work source content
    :type work_source_root: Path
    :param staging_root: root directory for staging the work's volumes
    :type staging_root: Path
    :type work_pms_item: pmItem
    :type volumes_pms_items: list[pmItem]
    """

    import shutil

    source_path: Path = c.get_work_image_path(work_source_root)
    staging_path: Path = c.get_work_image_path(staging_root)


    # always look on the bright side of liff
    work_pms_item.extras[c.PROJECT_STEP_RESULT_CODE_KEY] = 0        
    work_pms_item.extras[c.PROJECT_STEP_START_TIME_KEY] = pendulum.now("UTC")
    for volume_pms_item in volumes_pms_items:
        step_rc: int = -1

        try:
            # We're actually doing it! 
            output_dir = staging_path 
            output_dir.mkdir(parents=True, exist_ok=True)
            volume_pms_item.extras[c.PROJECT_STEP_START_TIME_KEY] = pendulum.now("UTC")
            shutil.copytree(source_path, output_dir, dirs_exist_ok=True)
            logger.info(
                f"Staged volume {volume_pms_item.label} {source_path=} {output_dir=}"
                f" (id={volume_pms_item.o_id}) to {output_dir}")
            step_rc = 0
        except Exception as e:
            logger.error(f"Error staging volume {volume_pms_item.label} (id={volume_pms_item.o_id}): {e}")
            step_rc = -1
        finally:
            # Update PMS with end time and result
            volume_pms_item.extras["project_step_end_time"] = pendulum.now("UTC")
            volume_pms_item.extras["project_step_result_code"] = step_rc # failure

    work_pms_item.extras["project_step_result_code"] = (
        -1 if any(v.extras.get("project_step_result_code", -1) != 0 for v in volumes_pms_items) else 0
    )
    work_pms_item.extras["project_step_end_time"] = pendulum.now("UTC")

    return work_pms_item

if __name__ == "__main__":
    # For testing
    stage_next_work('/Users/jkatz/tmp/DRS3/Archive', '/Users/jkatz/tmp/DRS3/staging')