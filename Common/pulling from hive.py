#make dictionary of items by their partitions
#this example can be applied to any of table in hive

from pyhive import presto
import pandas as pd
import numpy as np
import math
from joblib import Parallel
import joblib



#PARITION FORMULA
ITEM_PART= np.array((target_item_ids // 10000) + 1)
dic = {}

for item_part, id in zip(ITEM_PART, target_item_ids):
    if not item_part in dic:
        dic[item_part] = [id]
    else:
        dic[item_part].append(id)
for part, ids in dic.items():

    if len(ids) == 1:
        print(part)


#for multi-processing
def retrieve_from_presto(item_part, select_ids):
    select_ids = tuple(select_ids)
    
    if np.random.rand(1)>0.30: return
        
    if len(select_ids) > 1:
        hql_ivt = """
        SELECT item_id, stock_id, stock_amount, collect_day
        FROM inventory_part
        WHERE item_part = {} AND
        item_id IN {}
        """.format(item_part, select_ids)
    else:
        hql_ivt = """
        SELECT item_id, stock_id, stock_amount, collect_day
        FROM inventory_part
        WHERE item_part = {} AND
        item_id = {}
        """.format(item_part, select_ids[0])
        
    result = pd.read_sql_query(hql_ivt, engine_presto)
    result.to_parquet('directory/{}.parquet'.format(item_part), compression='gzip', engine='pyarrow')


#connect to presto 
engine_presto = presto.connect('133.186.168.10')

#n_jobs indicates the number of cores to use
#if n_jobs equals -1, it uses all cores the instace(or computer) have
Parallel(n_jobs=-1)(joblib.delayed(retrieve_from_presto) (item_part, select_ids) for item_part, select_ids in dic.items())