# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""

import os

import pendulum
from airflow import DAG
from airflow.sdk import task
from staging_utils import stage_next_work

# File paths Must exist in docker. See docker-compose
# Also, these statements are executed at dag parse time, 
# so copying the references is valid in any module
os.environ.setdefault("DRS3_SRC_ROOT", "/mnt/Archive")
os.environ.setdefault("DRS3_STAGING_ROOT", "/mnt/staging")
os.environ.setdefault("DRS3_STAGE_WORKS_MAX_ACTIVE_RUNS", "4")

SRC_ROOT = os.environ["DRS3_SRC_ROOT"]
STAGING_ROOT = os.environ["DRS3_STAGING_ROOT"]
MAX_ACTIVE_RUNS = int(os.environ["DRS3_STAGE_WORKS_MAX_ACTIVE_RUNS"])

with DAG(
    dag_id='drs3_stage_works',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    max_active_runs=MAX_ACTIVE_RUNS,
    tags=["staging", "works", "volumes", "drs3"],
) as dag:
    try:
        from airflow.sdk import get_current_context
    except ImportError:
        from airflow.operators.python import get_current_context

    @task
    def stage_next_work_task():
        context = get_current_context()
        dag_run = context.get("dag_run")
        dag_run_conf = dag_run.conf if dag_run else {}
        work_name = dag_run_conf.get("work_name")
        stage_next_work(SRC_ROOT, STAGING_ROOT, work_name=work_name)

    stage_next_work_task()
