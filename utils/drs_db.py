"""
Use BDRC ORM to get works which that have volumes that have not been deposited into DRS. 
Assume that all possible proce
"""

import logging
from typing import cast

import const as c
from BdrcDbLib.DrsContext import DrsDbContext
from BdrcDbModels.project_manager import ProjectMemberSteps, Projects, Steps
from sqlalchemy import Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def create_drs3_project_with_steps(session: Session):
    # Create the project
    
    # Only insert the DRS3 project if it does not already exist
    existing_project = session.query(Projects).filter_by(name=c.DRS3_PROJECT_NAME).first()
    if existing_project:
        print(f"{c.DRS3_PROJECT_NAME} project already exists, skipping creation.")
#        return existing_project
    else:
        project: Projects = Projects(name=c.DRS3_PROJECT_NAME, description=c.DRS3_PROJECT_DESC) # type: ignore
        session.add(project)
        session.flush()  # To get project.id
        existing_project = project

    # Define step names
    step_names = [c.STAGE_STEP_NAME, c.TRANSCODE_STEP_NAME, c.UPLOAD_STEP_NAME, c.PUBLISH_CONFIRM_STEP_NAME]

    # Create steps and link to project
    for step_name in step_names:
        existing_step = session.query(Steps).filter_by(s_name=step_name).first()
        if existing_step:
            print(f"Step '{step_name}' already exists, skipping creation.")
        else:
            existing_step = Steps(s_name=step_name, s_desc=f"{step_name} step")# type: ignore
            session.add(existing_step)
            session.flush()  # To get step.id

        session.flush()  # To get step.id

    session.commit()

try:
    # Create the steps and ProjectMemberSteps tables
    with DrsDbContext('RDSAWSQASA') as drs:
        drs_session = drs.get_session()
        if drs_session is None:
            raise ValueError("Failed to get a valid database session")

        # If the table defined in Steps, project member steps does not exist, create it
        engine = drs.get_engine()
        if not engine.dialect.has_table(engine.connect(), Steps.__tablename__): # pyright: ignore[reportOptionalMemberAccess]   
            cast(Table, Steps.__table__).create(bind=engine) # type: ignore
        if not engine.dialect.has_table(engine.connect(), ProjectMemberSteps.__tablename__):# pyright: ignore[reportOptionalMemberAccess]
            cast(Table, ProjectMemberSteps.__table__).create(bind=engine) # type: ignore
except SQLAlchemyError as e:
    logging.error(f"Error occurred: {e}")

with DrsDbContext('qa') as drs:
    drs_session = drs.get_session()
    if drs_session is None:
        raise ValueError("Failed to get a valid database session")
    create_drs3_project_with_steps(drs_session)
