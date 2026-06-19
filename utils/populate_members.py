import logging
import sys
from pathlib import Path

from archive_ops.api import get_archive_location
from BdrcDbLib.DrsContext import DrsDbContext
from BdrcDbModels.models import Volumes, Works
from BdrcDbModels.project_manager import MemberTypes, ProjectMembers, Projects
from BdrcDbModels.SqlAlchemy_get_or_create import get_or_create
from sqlalchemy import select
from sqlalchemy.orm import Session

MY_DB = 'qa'

logger = logging.getLogger(__name__)

if not logger.handlers:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(stream_handler)

logger.setLevel(logging.INFO)


def _select_member_type(session, m_type: str) -> MemberTypes:
    return session.execute(
        select(MemberTypes).where(MemberTypes.m_type == m_type)
    ).scalars().first()

def populate_members(archive_root: str, work_names: list[str],):
     
        with DrsDbContext(MY_DB) as db:
            session: Session = db.get_session()

            work_member_type: MemberTypes = _select_member_type(session, 'work')
            volume_member_type: MemberTypes = _select_member_type(session, 'volume')
            project = session.execute(
                select(Projects).where(Projects.name == 'DRS3')
            ).scalars().first()
            for work_name in work_names:
                # Locate work path using bdrc-utils (pseudo-code)
                # work_path = get_mappings(archive_root, work_name)
                # Create ProjectMember for work
                
                work = session.execute(
                    select(Works).where(Works.WorkName == work_name)
                ).scalars().first()
                if not work:
                    continue
                w_pm, is_new = get_or_create(session, ProjectMembers,
                    pm_type=work_member_type,
                    project=project,
                    work = work,
                    volume = None
                )
                act: str = "Added" if is_new else "Found"
                logger.info(f"{act} work member for {work_name} in project {project.name}")
                
                # For each volume under images/
                images_dir = Path(get_archive_location(archive_root, work_name)) / 'images'
                if images_dir.exists():
                    for vol_dir in images_dir.iterdir():
                        if vol_dir.is_dir():
                            # Lookup volumeId from Volumes table
                            volume_stmt =select(Volumes).where(Volumes.label == vol_dir.name) 

                            vol = session.execute(volume_stmt).scalars().first()
                            if not vol:
                                raise RuntimeError(
                                    f"Volume with label {vol_dir.name} not "
                                    f"found in database for work {work_name}"
                                )

                            v_pm, is_new = get_or_create(session, ProjectMembers,
                                pm_type=volume_member_type,
                                project=project,
                                # Have to add work here, to help find volumes that are not 
                                # processed. See get_pms_for_step()
                                work = work,
                                volume = vol
                            )
                            act: str = "Added" if is_new else "Found"
                            logger.info(f"{act} volume member for {vol_dir.name} in project {project.name}")
                session.commit()

if __name__ == "__main__":
    import os
    DATASET_PATH = os.environ.get("DRS3_DATASET_PATH", "~/tmp/DRS3/dataset.txt")
    ARCHIVE_ROOT = os.environ.get("DRS3_ARCHIVE_ROOT", "~/tmp/DRS3/Archive")
    dataset_path = os.path.expanduser(DATASET_PATH)
    archive_root = os.path.expanduser(ARCHIVE_ROOT)
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
    with open(dataset_path) as f:
        work_names = [line.strip() for line in f if line.strip()]
    populate_members(archive_root, work_names)