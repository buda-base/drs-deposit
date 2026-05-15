"""
DAG to populate ProjectMembers from a dataset file, as specified in Architecture.md.
"""
import os
from airflow import DAG
from airflow.decorators import task
from airflow.sensors.filesystem import FileSensor
from datetime import datetime
import pendulum
from pathlib import Path
import BdrcDbModels.project_manager as pm
from BdrcDbLib.DrsContext import DrsDbContext

DATASET_PATH = os.environ.get("DRS3_DATASET_PATH", "~/tmp/DRS3/dataset.txt")
ARCHIVE_ROOT = os.environ.get("DRS3_ARCHIVE_ROOT", "~/tmp/DRS3/Archive")

with DAG(
    dag_id='drs3_populate_projectmembers',
    schedule=None,
    start_date=pendulum.datetime(2026, 5, 15, tz="UTC"),
    catchup=False,
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
        dataset_path = os.path.expanduser(DATASET_PATH)
        archive_root = os.path.expanduser(ARCHIVE_ROOT)
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")
        with open(dataset_path) as f:
            work_names = [line.strip() for line in f if line.strip()]
        with DrsDbContext('qa') as db:
            session = db.get_session()
            for work_name in work_names:
                # Locate work path using bdrc-utils (pseudo-code)
                # work_path = get_mappings(archive_root, work_name)
                # Create ProjectMember for work
                work = session.query(pm.Works).filter_by(WorkName=work_name).first()
                if not work:
                    continue
                pm_work = pm.ProjectMembers(
                    member_type='work',
                    workId=work.WorkId
                )
                session.add(pm_work)
                session.flush()
                # For each volume under images/
                images_dir = Path(archive_root) / work_name / 'images'
                if images_dir.exists():
                    for vol_dir in images_dir.iterdir():
                        if vol_dir.is_dir():
                            # Lookup volumeId from Volumes table
                            volume = session.query(pm.Volumes).filter_by(VolumeName=vol_dir.name).first()
                            if not volume:
                                continue
                            pm_vol = pm.ProjectMembers(
                                member_type='volume',
                                workId=work.WorkId,
                                volumeId=volume.VolumeId
                            )
                            session.add(pm_vol)
                session.commit()
    sense_dataset >> populate_projectmembers()