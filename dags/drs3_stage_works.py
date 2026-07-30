# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""

import os
from asyncio.log import logger
from typing import cast

import staging_utils as su
from airflow import DAG
from airflow.sdk import get_current_context, task
from airflow.sdk.exceptions import AirflowFailException
from project_manager_utils import pmItem

# File paths Must exist in docker. See docker-compose
# Also, these statements are executed at dag parse time, 
# so copying the references is valid in any module.
# Note, this is a fallback - these values really should be set in
# the docker-compose file
os.environ.setdefault("DRS3_SRC_ROOT", "/mnt/Archive")
os.environ.setdefault("DRS3_STAGING_ROOT", "/mnt/staging")
os.environ.setdefault("DRS3_STAGE_WORKS_MAX_ACTIVE_RUNS", "4")

SRC_ROOT = os.environ["DRS3_SRC_ROOT"]
STAGING_ROOT = os.environ["DRS3_STAGING_ROOT"]
MAX_ACTIVE_RUNS = int(os.environ["DRS3_STAGE_WORKS_MAX_ACTIVE_RUNS"])

STAGING_OUTPUT

with DAG(
    dag_id='drs3_stage_works',
    # schedule=None,
    # start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    max_active_runs=MAX_ACTIVE_RUNS,
    tags=["staging", "works", "volumes", "drs3"],
) as dag:

    @task
    def stage_next_work_task():
        context = get_current_context()
        dag_run = context.get("dag_run")
        dag_run_conf = dag_run.conf if dag_run else {}
        work_name : str = cast(str, dag_run_conf.get("work_name"))  # pyright: ignore[reportOptionalMemberAccess]
        try:
            work_pmItem: pmItem | None 
            #
            # Ok, we're doing real work now.
            work_pmItem = su.stage_work(SRC_ROOT, STAGING_ROOT, work_name=work_name)
            step_rc = work_pmItem.extras.get("project_step_result_code", -1) if work_pmItem else -1
        finally:
            if step_rc != 0:
                logger.exception(f"Error staging work {work_pmItem.label} (id={work_pmItem.o_id}) {step_rc=}")
                raise AirflowFailException(f"Error staging {work_name=}: {step_rc}")

    stage_next_work_task()
     