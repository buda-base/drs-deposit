"""
DAG to stage works and volumes, as specified in Architecture.md.
"""
import os
from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import pendulum
from pathlib import Path
import BdrcDbModels.project_manager as pm
from BdrcDbLib.DrsContext import DrsDbContext
from dags.drs_utils import stage_content

STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "~/tmp/DRS3/staging")

with DAG(
    dag_id='drs3_stage_works',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
) as dag:
    @task
    def stage_next_work():
        staging_root = os.path.expanduser(STAGING_ROOT)
        with DrsDbContext('qa') as db:
            session = db.get_session()
            # Query for ProjectMembers of type 'Work' with no child volumes that have ProjectMemberSteps
            work = session.query(pm.ProjectMembers).filter(
                pm.ProjectMembers.member_type=='work',
                ~pm.ProjectMembers.volumes.any(
                    pm.ProjectMembers.member_type=='volume',
                    pm.ProjectMembers.projectmembersteps.any()
                )
            ).first()
            if not work:
                return 'No eligible work found.'
            # Create ProjectMemberStep for the volume of type 'staged'
            for volume in work.volumes:
                pms = pm.ProjectMemberSteps(
                    projectmember_id=volume.id,
                    step='staged',
                )
                session.add(pms)
                session.flush()
                # Stage content
                output_dir = Path(staging_root) / str(work.workId)
                output_dir.mkdir(parents=True, exist_ok=True)
                stage_content(Path(volume.path), output_dir)
                # Update PMS with end time and result
                pms.end_time = datetime.utcnow()
                pms.result_code = 0
            session.commit()
            # Check if all volumes are staged
            all_staged = all(
                v.projectmembersteps and any(s.step=='staged' and s.result_code==0 for s in v.projectmembersteps)
                for v in work.volumes
            )
            if all_staged:
                pms_work = pm.ProjectMemberSteps(
                    projectmember_id=work.id,
                    step='staged',
                    end_time=datetime.utcnow(),
                    result_code=0
                )
                session.add(pms_work)
                session.commit()
        return 'Staging complete.'
    stage_next_work()