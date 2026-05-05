"""
Use BDRC ORM to get works which that have volumes that have not been deposited into DRS. 
Assume that all possible proce
"""
import BdrcDbLib.DbOrm
from requests import session

print(dir(BdrcDbLib.DbOrm))


from  BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase 
from BdrcDbModels.project_manager import Projects, Steps, ProjectSteps
from sqlalchemy.orm import Session


def create_drs3_project_with_steps(session: Session):
    # Create the project
    
    project: Projects = Projects(name="DRS3", description="DRS3 project") # type: ignore
    session.add(project)
    session.flush()  # To get project.id

    # Define step names
    step_names = ["transcode", "upload", "Check for upload completed"]

    # Create steps and link to project
    for name in step_names:
        step = Steps(s_name=name, s_desc=f"{name} step")# type: ignore
        session.add(step)
        session.flush()  # To get step.id

        project_step = ProjectSteps(ps_project=project.id)# type: ignore
        session.add(project_step)

    session.commit()
    return project

with DrsDbContextBase('qa') as drs:
    session = drs.get_session()
    if session is None:
        raise ValueError("Failed to get a valid database session")
    create_drs3_project_with_steps(session)
