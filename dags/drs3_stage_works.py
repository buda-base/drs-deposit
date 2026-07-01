# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""

import os

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.sdk import Asset
from staging_utils import stage_next_work

# Must exist in docker. See docker-compose
SRC_ROOT = "/mnt/Archive"
STAGING_ROOT = os.environ.get("DRS3_STAGING_ROOT", "/mnt/staging")
DRS3_STAGE_WORKS_ASSET = Asset("drs3://candidate_works/changed")

with DAG(
    dag_id='drs3_stage_works',
    schedule=[DRS3_STAGE_WORKS_ASSET],
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    tags=["staging", "works", "volumes", "drs3"],
) as dag:
    @task
    def stage_next_work_task():
        stage_next_work(SRC_ROOT, STAGING_ROOT)

    stage_tasks = [
        stage_next_work_task.override(task_id=f"stage_next_work_task_{i}")()
        for i in range(1, 4)
    ]
