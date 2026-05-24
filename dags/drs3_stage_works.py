# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""
import os
from airflow import DAG

import pendulum
from pathlib import Path
import utils.staging_utils as utils

with DAG(
    dag_id='drs3_stage_works',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
) as dag:
    @dag.task
    def stage_next_work():
        utils.stage_next_work()

 
    stage_next_work()
