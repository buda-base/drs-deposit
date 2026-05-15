"""
Use BDRC ORM to get works which that have volumes that have not been deposited into DRS. 
Assume that all possible proce
"""
import  BdrcDbModels.project_manager as pm


from   BdrcDbLib.DrsContextBase import DrsDbContextBase
# from BdrcDbModels.project_manager import Projects, Steps, ProjectSteps, ProjectMemberSteps
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
    
import logging


def create_drs3_project_with_steps(session: Session):
    # Create the project
    
    # Only insert the DRS3 project if it does not already exist
    existing_project = session.query(pm.Projects).filter_by(name="DRS3").first()
    if existing_project:
        print("DRS3 project already exists, skipping creation.")
#        return existing_project
    else:
        project: pm.Projects = pm.Projects(name="DRS3", description="DRS3 project") # type: ignore
        session.add(project)
        session.flush()  # To get project.id
        existing_project = project

    # Define step names
    step_names = ["stage", "transcode", "upload", "publish_confirm"]

    # Create steps and link to project
    for step_name in step_names:
        existing_step = session.query(pm.Steps).filter_by(s_name=step_name).first()
        if existing_step:
            print(f"Step '{step_name}' already exists, skipping creation.")
        else:
            existing_step = pm.Steps(s_name=step_name, s_desc=f"{step_name} step")# type: ignore
            session.add(existing_step)
            session.flush()  # To get step.id

        # Add this step to the project steps
        project_step = pm.ProjectSteps(ps_project_id=existing_project.id, ps_step_id=existing_step.id)  # pyright: ignore[reportCallIssue]
        session.add(project_step)
        session.flush()  # To get step.id

    session.commit()

try:
    with DrsDbContextBase('RDSAWSQASA') as drs:
        drs_session = drs.get_session()
        if drs_session is None:
            raise ValueError("Failed to get a valid database session")

        # If the table defined in Steps, project member steps does not exist, create it
        engine = drs.get_engine()
        if not engine.dialect.has_table(engine.connect(), pm.Steps.__tablename__): # pyright: ignore[reportOptionalMemberAccess]   
            pm.Steps.__table__.create(bind=engine)
        if not engine.dialect.has_table(engine.connect(), pm.ProjectSteps.__tablename__):# pyright: ignore[reportOptionalMemberAccess]
            pm.ProjectSteps.__table__.create(bind=engine)
        if not engine.dialect.has_table(engine.connect(), pm.ProjectMemberSteps.__tablename__):# pyright: ignore[reportOptionalMemberAccess]
            pm.ProjectMemberSteps.__table__.create(bind=engine)
except SQLAlchemyError as e:
    logging.error(f"Error occurred: {e}")

with DrsDbContextBase('qa') as drs:
    drs_session = drs.get_session()
    if drs_session is None:
        raise ValueError("Failed to get a valid database session")
    create_drs3_project_with_steps(drs_session)
