#functions concerned with directory in python
#the following directory is shared among workers (airflow)


os.chdir("/app/dev/airflow/reposit") #change directory
os.path.isdir() #whether a directory exist or not
os.makedirs() #make directory
os.remove #remove directory
