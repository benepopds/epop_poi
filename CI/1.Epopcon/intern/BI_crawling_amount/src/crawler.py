from src.cm import *

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'owner' : 'geuntaek',
    'depends_on_past':False,
    'start_date':datetime(2018,7,11),
    'retries':5,
    'retry_delay':timedelta(minutes=1)     
}



dag = DAG('CRAWLING_MONITOR',
         default_args = default_args,
         dagrun_timeout=timedelta(days=1),
         description="CRAWLING_MONITOR",
         schedule_interval='00 23 * * *')

crawl_operator = PythonOperator(
        task_id='CRAWLING_MONITOR',
        python_callable=my_main,                
        queue='q_development',
        dag=dag)

waiting_operator = BashOperator(
        task_id = 'sleep',
        bash_command='sleep 1',
        queue='q_development',
        dag=dag)


waiting_operator >> crawl_operator

