from airflow import DAG
from airflow.decorators import task
from datetime import datetime
import pendulum
import os

with DAG(
    dag_id='hoopsty_dataset_checker',
    # schedule='@hourly',
    schedule=None,
    start_date=pendulum.datetime(2026, 4, 26, tz="UTC"),
    catchup=False,
) as dag:

    @task
    def check_dataset():
        # not in docker
        # import debugpy; 
        # debugpy.listen(5678); debugpy.wait_for_client()
        
        target_dir = "dags/simple_dag.py"
        target_file = "data.txt"
        file_path = os.path.join(target_dir, target_file)
        
        exists = os.path.isfile(file_path)
        print(f"Checking for {file_path}: {'Found' if exists else 'Not Found'}")
        return exists

    check_dataset()

if __name__ == "__main__":
    dag.test()