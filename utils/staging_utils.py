# pyright: reportArgumentType=false
# avoid warning for TIMESTAMP mapped columns (e.g. ..start_time )
"""
Supports DAG. Extracted for testing
"""

import os
from pathlib import Path

import pendulum
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from BdrcDbModels.models import (
    Works,
    Volumes
)
from BdrcDbModels.project_manager import (
    Projects,
    Steps,
    ProjectMembers,
    MemberTypes,
    ProjectMemberSteps,
)

from BdrcDbLib.DrsContext import DrsDbContext
from utils.drs_utils import stage_content
import const as c


STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "~/tmp/DRS3/staging")

MY_DB = 'qa'  # or 'prod' in production

def _get_drs3_project_objects() :    
    with DrsDbContext(MY_DB) as db:
        session = db.get_session()
        project_named_drs3 =  select(Projects).where(Projects.name == c.DRS3_PROJECT_NAME)  # pyright: ignore[reportArgumentType]
        project = session.execute(project_named_drs3).scalar_one_or_none()
        if not project:
            raise RuntimeError(f"{c.DRS3_PROJECT_NAME} project not found")

        get_work_type_work = select(MemberTypes).where(MemberTypes.m_type == c.PROJECT_MEMBER_TYPE_WORK)  # pyright: ignore[reportArgumentType]
        work_type = session.execute(get_work_type_work).scalar_one_or_none()
        if not work_type:
            raise RuntimeError(f"{c.PROJECT_MEMBER_TYPE_WORK} MemberType not found")  
        
        volume_type = session.execute(
            select(MemberTypes).where(
                MemberTypes.m_type == c.PROJECT_MEMBER_TYPE_VOLUME
            )
        ).scalar_one_or_none()
        if not volume_type:
            raise RuntimeError(f"{c.PROJECT_MEMBER_TYPE_VOLUME} MemberType not found")
        
        staging_step = session.execute(
            select(Steps).where(
                Steps.s_name == c.STAGE_STEP_NAME
            )
        ).scalar_one_or_none()
        if not staging_step:
            raise RuntimeError(f"{c.STAGE_STEP_NAME} Step not found")

    
        return project, work_type, volume_type


DRS3_PROJECT, DRS3_WORK_TYPE, DRS3_VOLUME_TYPE = _get_drs3_project_objects()

def get_next_unstaged_work():
    with DrsDbContext(MY_DB) as db:
        session = db.get_session()
        # Select Work project members where no child volume has any ProjectMemberSteps
        next_work = session.execute(
            select(ProjectMembers).where(
                ProjectMembers.project == DRS3_PROJECT,
                ProjectMembers.type == DRS3_WORK_TYPE,
                ~ProjectMembers.volume.any(
                    ProjectMembers.project_member_steps.any()
                ),
            )
        ).scalars().first()
        return next_work.id if next_work else None

def stage_next_work():
    staging_start_time: pendulum.DateTime = pendulum.now("UTC")
    staging_root = os.path.expanduser(STAGING_ROOT)

    staged_pms_id: int = -1
    with DrsDbContext(MY_DB) as db:
        session = db.get_session()

        # Get references for ProjectMemberSteps
        # Get the Step for staging
        staged_step = session.execute(
            select(Steps).where(Steps.s_name == c.STAGE_STEP_NAME)
        ).scalar_one_or_none()
        if not staged_step:
            raise RuntimeError(f"{c.STAGE_STEP_NAME} step not found")
        
        
        # Query for ProjectMembers of type 'Work' with no child volumes that have ProjectMemberSteps

        get_work_select =    select(ProjectMembers).where(
                ProjectMembers.type == DRS3_WORK_TYPE,
                ~ProjectMembers.volume.any(
                    and_(
                        ProjectMembers.type == DRS3_VOLUME_TYPE,
                        ~ProjectMembers.project_member_steps.any()
                    )
                )
            )
        unstaged_work_pm : ProjectMembers | None = session.execute(get_work_select).scalars().first()
        if not unstaged_work_pm:
            return 'No eligible work found.'
        # Create ProjectMemberStep for the volume of type 'staged'
        unstaged_work: Works | None = unstaged_work_pm.work
        if not unstaged_work:
            raise RuntimeError(f"Work not found for ProjectMember id {unstaged_work_pm.id}")

        for volume in unstaged_work.volumes:
            # select this volume from ProjectMembers
            volume_pm = session.execute(
                select(ProjectMembers).where(
                    ProjectMembers.project == DRS3_PROJECT,
                    ProjectMembers.type == DRS3_VOLUME_TYPE,
                    ProjectMembers.volume == volume
                )
            ).scalar_one_or_none()
            if not volume_pm:
                raise RuntimeError(f"Volume ProjectMember not found for Volume id {volume.volumeId}")

            volume_pms = ProjectMemberSteps(
                project_member = volume_pm,
                project_step = staged_step,
                project_step_start_time=pendulum.now("UTC"), 
            )
            session.add(volume_pms) # type: ignore
            session.commit()

#TODO: How to bust out of the context while keeping all the works and volumes in scope
            # Stage content
            output_dir = Path(staging_root) / str(work.workId)
            output_dir.mkdir(parents=True, exist_ok=True)
            stage_content(Path(volume.path), output_dir)
            # Update PMS with end time and result
            volume_pms.project_step_end_time = None  # pyright: ignore[reportArgumentType]
            volume_pms.project_step_result_code = 0
        session.commit()
        # Check if all volumes are staged
        # TODO: Test failure
        all_staged = all(
            v.project_member_steps
            and any(
                s.project_step_id == DRS3_STAGED_PROJECT_STEP_ID
                and s.project_step_result_code == 0
                for s in v.project_member_steps
            )
            for v in work.volumes
        )
        if all_staged:
            pms_work = ProjectMemberSteps(  # pyright: ignore[reportCallIssue]
                project_member_id=work.id,
                project_step_id=DRS3_STAGED_PROJECT_STEP_ID,
                project_step_start_time=staging_start_time,
                project_step_end_time=pendulum.now("UTC"),
                project_step_result_code=0
            )
            session.add(pms_work)
            session.commit()
    return 'Staging complete.'  