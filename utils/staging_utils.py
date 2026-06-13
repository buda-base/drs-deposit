# xxpyright: xxreportArgumentType=false
# avoid warning for TIMESTAMP mapped columns (e.g. ..start_time ) F401
"""
Supports DAG. Extracted for testing
"""

import logging
import os

import const as c
import pendulum
from BdrcDbLib.DrsContext import DrsDbContext
from BdrcDbModels.models import Volumes
from BdrcDbModels.project_manager import (
    MemberTypes,
    ProjectMembers,
    ProjectMemberSteps,
    Projects,
    Steps,
)
from BdrcDbModels.SqlAlchemy_get_or_create import get_or_create
from sqlalchemy import exists, select
from sqlalchemy.orm import Session, aliased

logger = logging.getLogger(__name__)

MY_DB = "qa"  # or 'prod' in production
STAGING_ROOT = os.path.expandvars(os.environ.get("DRS3_STAGING_ROOT","/mnt/staging"))


def _get_drs3_project_objects():
    """
    Pre-fetch some standard lookup model objects
    """
    with DrsDbContext(MY_DB) as db:
        session = db.get_session()
        project_named_drs3 = select(Projects).where(Projects.name == c.DRS3_PROJECT_NAME)  # pyright: ignore[reportArgumentType]
        project = session.execute(project_named_drs3).scalar_one_or_none()
        if not project:
            raise RuntimeError(f"{c.DRS3_PROJECT_NAME} project not found")

        get_work_type_work = select(MemberTypes).where(MemberTypes.m_type == c.PROJECT_MEMBER_TYPE_WORK)  # pyright: ignore[reportArgumentType]
        work_type = session.execute(get_work_type_work).scalar_one_or_none()
        if not work_type:
            raise RuntimeError(f"{c.PROJECT_MEMBER_TYPE_WORK} MemberType not found")

        volume_type = session.execute(
            select(MemberTypes).where(MemberTypes.m_type == c.PROJECT_MEMBER_TYPE_VOLUME)
        ).scalar_one_or_none()
        if not volume_type:
            raise RuntimeError(f"{c.PROJECT_MEMBER_TYPE_VOLUME} MemberType not found")

        staging_step = session.execute(select(Steps).where(Steps.s_name == c.STAGE_STEP_NAME)).scalar_one_or_none()
        if not staging_step:
            raise RuntimeError(f"{c.STAGE_STEP_NAME} Step not found")

        return project, work_type, volume_type, staging_step


DRS3_PROJECT, DRS3_WORK_TYPE, DRS3_VOLUME_TYPE, DRS3_STAGING_STEP = _get_drs3_project_objects()


def get_next_unstaged_work():
    with DrsDbContext(MY_DB) as db:
        session: Session = db.get_session()

        def _load_relationships(obj, seen: set[int]) -> None:
            """
            Recursively load all relationships of this object, to avoid lazy loading after the session is closed.
            GitHubCopilot generated
            """
            from sqlalchemy import inspect

            if obj is None:
                return
            oid = id(obj)
            if oid in seen:
                return
            seen.add(oid)

            mapper = inspect(obj).mapper
            for rel in mapper.relationships:
                # This triggers the query that will load the relationship if it is not already loaded,
                # and does nothing if it is already loaded. We need to do this for all relationships,
                # even those we don't
                # directly use, to avoid lazy loading after the session is closed.
                value = getattr(obj, rel.key)
                if value is None:
                    continue
                if rel.uselist:
                    for child in value:
                        _load_relationships(child, seen)
                else:
                    _load_relationships(value, seen)

        # Select Work project members where no child volume has any ProjectMemberSteps

        WorkPM = aliased(ProjectMembers)
        VolumePM = aliased(ProjectMembers)

        # Github copilot claims:
        # This returns a work-level ProjectMembers row for DRS3 where there is no ProjectMemberSteps
        # row attached to any volume whose Volumes.workId matches that work.
        stmt = (
            select(WorkPM)
            .where(
                WorkPM.project == DRS3_PROJECT, 
                WorkPM.pm_type == DRS3_WORK_TYPE,
                ~exists(
                    select(1)
                    .select_from(ProjectMemberSteps)
                    .join(VolumePM, ProjectMemberSteps.project_member_id == VolumePM.id)
                    .join(Volumes, VolumePM.pm_volume_id == Volumes.volumeId)
                    .where(
                        VolumePM.project == DRS3_PROJECT,
                        VolumePM.pm_type == DRS3_VOLUME_TYPE,
                        Volumes.workId == WorkPM.pm_work_id,  # correlate to outer work PM
                    )
                ),
            )
            .limit(1)
        )

        next_work_pm = session.scalars(stmt).first()
        if not next_work_pm:
            logger.info("No unstaged work found")
            return None

        # Create the ProjectMemberStep for this work
        # Bug - for sql get or create, you only supply the key fields
        # in the call - because all parameters are searched for, including
        # runtime constructs
        work_pms, is_new = get_or_create(
            session,
            ProjectMemberSteps,
            project_member=next_work_pm,
            project_step=DRS3_STAGING_STEP,
        )

        status_: str = f"ProjectMemberSteps for work {next_work_pm.work.WorkName}"
        if is_new:
            logger.info(f"Created {status_}")
            work_pms.project_step_start_time = pendulum.now("UTC")
        else:
            logger.info(f"Found {status_}")
        session.commit()

        # Fully load relationships, then detach so it can be used after context closes.
        _load_relationships(next_work_pm, set())
        return next_work_pm


def get_pms_to_stage(unstaged_work_pm: ProjectMembers) -> tuple[ProjectMemberSteps, list[ProjectMemberSteps]]:
    """
    Get or create all the ProjectMemberSteps for the volumes of this work
    that need to be staged, and return them as a list
    :param unstaged_work_pm: the ProjectMembers instance for the work to stage
    :type unstaged_work_pm: ProjectMembers
    :return: list of ProjectMemberSteps for the volumes to stage
    :rtype: list[ProjectMemberSteps]
    Note this list is detached from its connection. You can attributes of list elements in place, outside of a context
    When you want to update, iterate over the list in  a DrsDbContext, merge each item, and commit the session
    """
    unstaged_volumes_pms: list[ProjectMemberSteps] = []
    with DrsDbContext(MY_DB) as db:
        session: Session = db.get_session()

        # Create the staged step for the work ProjectMember and set start time to now
        unstaged_work_pms: ProjectMemberSteps 
        unstaged_work_pms, is_new = get_or_create(
            session,
            ProjectMemberSteps,
            project_member=unstaged_work_pm,
            project_step=DRS3_STAGING_STEP
        )
        unstaged_work_pms.project_step_start_time = pendulum.now("UTC")
        session.flush()

        for volume in unstaged_work_pm.work.volumes:
            # select this volume from ProjectMembers

            volume_pm = session.execute(
                select(ProjectMembers).where(
                    ProjectMembers.project == DRS3_PROJECT,
                    ProjectMembers.pm_type == DRS3_VOLUME_TYPE,
                    ProjectMembers.volume == volume,
                    ProjectMembers.work == unstaged_work_pm.work,
                )
            ).scalar_one_or_none()
            if not volume_pm:
                raise RuntimeError(f"Volume ProjectMember not found for Volume id {volume.volumeId}")
            session.flush()

            volume_pms, is_new = get_or_create(
                session,
                ProjectMemberSteps,
                project_member=volume_pm,
                project_step=DRS3_STAGING_STEP

            )
            volume_pms.project_step_start_time = pendulum.now("UTC")
            session.flush()
            unstaged_volumes_pms.append(volume_pms)
        session.commit()

    return unstaged_work_pms, unstaged_volumes_pms


def stage_next_work(source_root: str, staging_root: str) -> ProjectMembers:
    """
    Finds the next unstaged work from the project, creates the ProjectMemberSteps 
    for the work and its volumes, and stages the content for each volume.
    :param source_root: root directory for source content
    :param staging_root: root directory for staging
    :type source_root: str
    :type staging_root: str
    :return: ProjectMembers instance for the work being staged
    :rtype: ProjectMembers
    """

    work_to_stage_pm : ProjectMembers = get_next_unstaged_work()
    if not work_to_stage_pm:
        return

    unstaged_work_pms: ProjectMemberSteps
    unstaged_volumes_pms: list[ProjectMemberSteps] 
    unstaged_work_pms, unstaged_volumes_pms = get_pms_to_stage(work_to_stage_pm)
    if not unstaged_volumes_pms:
        raise RuntimeError(f"No volumes to stage for work {work_to_stage_pm.id}")
    try:

        # always look on the bright side of life
        unstaged_work_pms.project_step_result_code = 0
        do_staging(unstaged_work_pms, unstaged_volumes_pms, source_root, staging_root)
    except Exception as e:
        logger.error(f"Error staging work {work_to_stage_pm.id}: {e}")

        # Maybe partial success
        unstaged_work_pms.project_step_result_code = 1
    finally:        
        complete_staging(unstaged_work_pms, unstaged_volumes_pms)
    return work_to_stage_pm


def complete_staging(work_pms: ProjectMemberSteps, volume_pms_s: list[ProjectMemberSteps]):
    """
    :param volume_pms_s: list of ProjectMemberSteps for the volumes that were staged, updated out of context.
    :type volume_pms_s: list[ProjectMemberSteps]

    """
    work_pms.project_step_end_time = pendulum.now("UTC")

    with DrsDbContext(MY_DB) as db:
        session = db.get_session()
        for v_pms in volume_pms_s:
            session.merge(v_pms)
        session.merge(work_pms)
        session.commit()
    session.commit()


def do_staging(
    work_pms: ProjectMemberSteps,
    volumes_pms: list[ProjectMemberSteps],
    source_root: str, staging_root: str) -> None:
    """
    Stage mainline
    :param work_pms: the ProjectMemberSteps for the work being staged, updated out of context
    :param volumes_pms: list of ProjectMemberSteps for the volumes being staged, updated out of context
    :param staging_root: root directory for staging
    :param source_root: root directory for source
    :type work_pms: ProjectMemberSteps
    :type volumes_pms: list[ProjectMemberSteps]
    :type staging_root: str
    :return: status message
    :rtype: str
    """

    import shutil
    from pathlib import Path

    from bdrc_utils.archive_ops.api import get_archive_location

    work_name: str = work_pms.project_member.work.workName
    source_path: Path = Path(get_archive_location(source_root,work_name)) / 'images'
    staging_path: Path = Path(staging_root) / work_name  

    for pm_volume in volumes_pms:
        step_rc: int = -1
        volume: Volumes = pm_volume.project_member.volume

        try:
            # We're actually doing it! 
            output_dir = staging_path 
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source_path, output_dir, dirs_exist_ok=True)
            step_rc = 0
        except Exception as e:
            logger.error(f"Error staging volume {volume.volumeId}: {e}")
            step_rc = -1
        finally:
            # Update PMS with end time and result
            pm_volume.project_step_end_time = pendulum.now("UTC")
            pm_volume.project_step_result_code = step_rc # failure

if __name__ == "__main__":
    # For testing
    stage_next_work('/Users/jkatz/tmp/DRS3/Archive', '/Users/jkatz/tmp/DRS3/staging')