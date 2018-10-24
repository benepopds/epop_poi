from sqlalchemy import create_engine
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
from pyhive import presto
from joblib import Parallel
import joblib
import glob
from dask import delayed
import datetime
import glob
from tqdm import tqdm,trange,tqdm_notebook
import math
from operator import itemgetter, attrgetter, methodcaller
from pytz import timezone
import os
import gc
from dateutil.relativedelta import relativedelta
import time
import pickle



def retrieve_ids(site_hive):
    #retrieve all item_id from given site
    engine_presto = presto.connect('133.186.168.10')
    today = datetime.datetime.today()

    query= """
    select id as ITEM_ID, item_num as ITEM_NUM
    from item_part
    where site_name = '{}'
    and upt_dt > '{}'
    limit 1000
    """.format(site_hive, (today-datetime.timedelta(days=23)).strftime("%Y-%m-%d"))

    recent_item = pd.read_sql_query(query,engine_presto)
    
    print("%s items are retrieved"%len(recent_item))
    return recent_item

def get_BS_URL_ids(site_hive, site_sql):
    start = time.time()
    engine = create_engine("mysql+pymysql://wspider:wspider00!q@192.168.0.36:3306/wspider", pool_size=20, pool_recycle=3600, connect_args={'connect_timeout': 1000000})
    query = """
    select ITEM_NUM, SELL_END_YN from MWS_COLT_BS_URL
    where COLLECT_SITE = '{}'
    and SELL_END_YN = 0
    """.format(site_sql)
    BS_URL = pd.read_sql_query(query, engine)
    end = time.time()
    print("Base URL table has {} rows whose SELL_END_YN = 0 for {} ({} minute)".format(len(BS_URL), site_hive, round((end-start)/60, 2)))
    return BS_URL

def SELL_FILTER(target_items, BS_URL, site_hive):
    target_in_sale = target_items.ITEM_NUM.isin(BS_URL.ITEM_NUM)
    print("%s items are dropped"%(sum(-target_in_sale)))

    os.chdir("/app/dev/airflow/reposit/")
    target_items[target_in_sale][['ITEM_ID']].to_pickle("item_ids_{}".format(site_hive))        
    return 

## main function
def apply_retrieving():
    #initialize for gsshop
    site_hive = "GSSHOP"
    site_sql  = 'www.gsshop.com'

    #get and save item_ids 
    target_items = retrieve_ids(site_hive)
    BS_URL = get_BS_URL_ids(site_hive, site_sql)
    SELL_FILTER(target_items, BS_URL, site_hive)
    return
