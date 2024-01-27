# import modules and classes
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime
from real_yo_realtor_etl import main 

# defines a dictionary default parameters for dag task
default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date': datetime(2024, 1, 23),
	'email': ['airflow@example.com'],
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 1,
	'retries_delay': timedelta(minutes=1)
}

# defines an Apache Airflow DAG (Directed Acyclic Graph) with 
# the identifier 'real_yo_realtor_dag'.
dag = DAG(
	'real_yo_realtor_dag',
	default_args=default_args,
	description='Building ETL for real-yo-realtor company'
)

# defines an Apache Airflow task using the PythonOperator
run_etl = PythonOperator(
	task_id='complete_real_yo_realtor_etl',
	python_callable=main,
	dag=dag,
)

# Execute PythonOperator task
run_etl