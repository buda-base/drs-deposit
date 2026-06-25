# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""

import pendulum
from airflow import DAG
from staging_utils import stage_next_work

SRC_ROOT= "/mnt/Archive"
STAGING_ROOT = "/Users/jkatz/tmp/DRS3/staging"

with DAG(
    dag_id='drs3_stage_works',
    schedule=None,
    start_date=None, # pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    tags=["staging", "works", "volumes", "drs3"],
) as dag:
    @dag.task
    def stage_next_work_task():
        stage_next_work(SRC_ROOT, STAGING_ROOT)

 
    stage_next_work_task()
