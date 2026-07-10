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
from airflow.sensors.time_delta import TimeDeltaSensor
from staging_utils import stage_next_work

# File paths Must exist in docker. See docker-compose
# Also, these statements are executed at dag parse time, 
# so copying the references is valid in any module
os.environ.setdefault("DRS3_SRC_ROOT", "/mnt/Archive")
os.environ.setdefault("DRS3_STAGING_ROOT", "/mnt/staging")
os.environ.setdefault("DRS3_STAGE_WORKS_ASSET_URI", "drs3://candidate_works/changed")

SRC_ROOT = os.environ["DRS3_SRC_ROOT"]
STAGING_ROOT = os.environ["DRS3_STAGING_ROOT"]
DRS3_STAGE_WORKS_ASSET = Asset(os.environ["DRS3_STAGE_WORKS_ASSET_URI"])

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

    # This should stagger the start of each stage task
    # in 30 second increments
    stage_tasks = []
    for i in range(1, 4):
        stage_task = stage_next_work_task.override(task_id=f"stage_next_work_task_{i}")()
        stage_tasks.append(stage_task)

        # stagger_start = TimeDeltaSensor(
        # ask_id=f"stagger_start_{i}",
        #     delta=pendulum.duration(seconds=(i - 1) * 30),
        # )
        # stage_task = stage_next_work_task.override(task_id=f"stage_next_work_task_{i}")()
        # stagger_start >> stage_task
        # stage_tasks.append(stage_task)
