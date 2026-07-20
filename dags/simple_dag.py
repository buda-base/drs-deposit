import os

from airflow import DAG
from airflow.sdk import task

with DAG(
    dag_id='hoopsty_dataset_checker',
    # schedule='@hourly',
    schedule=None,
    tags=["staging", "works", "volumes", "drs3"],
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
        #
        return exists

    check_dataset()

if __name__ == "__main__":
    dag.test()