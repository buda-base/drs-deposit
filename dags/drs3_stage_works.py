# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""

import os

import pendulum
from airflow import DAG
from airflow.sdk import get_current_context, task
from airflow.sdk.exceptions import AirflowFailException
from project_manager_utils import pmItem
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

    @task
    def stage_next_work_task():
        context = get_current_context()
        dag_run = context.get("dag_run")
        dag_run_conf = dag_run.conf if dag_run else {}
        work_name = dag_run_conf.get("work_name")
        try:
            work_pmItem: pmItem | None = stage_next_work(SRC_ROOT, STAGING_ROOT, work_name=work_name)
            if not work_pmItem:
                return None

            if work_pmItem.extras.get("project_step_result_code", -1) != 0:
                raise AirflowFailException(f"Error staging work {work_pmItem.label} (id={work_pmItem.o_id})")
        except Exception as e:
            raise AirflowFailException(f"Error staging work {work_name}: {e}") from e


    stage_next_work_task()
     