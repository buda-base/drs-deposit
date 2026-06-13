# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=true
"""
DAG to stage works and volumes, as specified in Architecture.md.
"""

import pendulum
from airflow import DAG

import utils.staging_utils as utils

SRC_ROOT= "/Users/jkatz/tmp/DRS3/Archive"
STAGING_ROOT = "/Users/jkatz/tmp/DRS3/staging"

with DAG(
    dag_id='drs3_stage_works',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
) as dag:
    @dag.task
    def stage_next_work():
        utils.stage_next_work(SRC_ROOT, STAGING_ROOT)

 
    stage_next_work()
