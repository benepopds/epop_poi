#This module filters non on-crawling items
#It uses SELL_END_YN column from MWS_COLT_BS_URL
#There are two problems

#Firstly, key column is ITEM_NUM, not ITEM_ID.
#Thus we retrieve ITEM_NUMs with SELL_END_YN=0 from MWS_COLT_BS_URL (RDBMS)
#And then, we retrieve all ITEM_ID and ITEM_NUM from item_part table in Hive using Presto
#We tried several things and its fastest and most stable!

#Second problem is that even if SELL_END_YN of a ITEM equals 0, crawling might be stopped (5~10%??)
#We can not distinguish it perfectly...
#But still, items with SELL_END_YN=1 is not on-crawling! (needed to be tested)


from sqlalchemy import create_engine
from pyhive import presto
import pandas as pd
import numpy as np
import math
import gc
import glob
import os
import datetime
import time

def get_BS_URL_ids():
    start = time.time()
    engine = create_engine("mysql+pymysql://wspider:wspider00!q@192.168.0.36:3306/wspider", pool_size=20, pool_recycle=3600, connect_args={'connect_timeout': 1000000})
    query = """
    select ITEM_NUM, SELL_END_YN from MWS_COLT_BS_URL
    where COLLECT_SITE = 'www.gsshop.com'
    """
    BS_URL = pd.read_sql_query(query, engine)
    end = time.time()
    print("Base URL table has %s rows for GSSHOP (%s minute)"%(len(BS_URL), round((end-start)/60, 2)))
    return BS_URL




def num_to_id(df):
	engine_presto = presto.connect('133.186.168.10')
    chunk_size = int(len(df)/10)
    ids = []
    for i in tqdm.tqdm_notebook(np.array_split(df.ITEM_NUM.values, chunk_size)):
        query = """
        select ID
        from MWS_COLT_ITEM 
        where ITEM_NUM in {}
        and 
        """.format(tuple(i))
        ids.append(pd.read_sql_query(query,engine)["ID"].values)

    return np.concatenate(ids).ravel()