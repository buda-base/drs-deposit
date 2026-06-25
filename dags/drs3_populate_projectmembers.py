"""
DAG to populate ProjectMembers from a dataset file, as specified in Architecture.md.
"""
import os
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.sensors.filesystem import FileSensor
from populate_members import populate_members

DATASET_PATH = os.environ.get("DRS3_DATASET_PATH", os.path.expanduser("~/tmp/DRS3/dataset.txt"))
ARCHIVE_ROOT = os.environ.get("DRS3_ARCHIVE_ROOT", os.path.expanduser("~/tmp/DRS3/Archive"))

with DAG(
    dag_id='drs3_populate_projectmembers',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
    tags=["project_members","drs3"],
) as dag:
    
    sense_dataset = FileSensor(
        task_id="sense_dataset",
        filepath=DATASET_PATH,
        poke_interval=60,
        timeout=600,
        mode="poke",
    )

    @task
    def populate_projectmembers():
        if not os.path.exists(DATASET_PATH):
            raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")
        with open(DATASET_PATH) as f:
            # Strip surrounding whitespace, and skip empty lines
            work_names = [line.strip() for line in f if line.strip()]
        populate_members(ARCHIVE_ROOT, work_names)
        
    sense_dataset >> populate_projectmembers()