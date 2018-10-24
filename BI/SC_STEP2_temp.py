from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.base import clone
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.utils import shuffle
import statsmodels.api as sm


def retrieve_from_presto(item_part, select_ids, today, last_month, drt):
    select_ids = tuple(select_ids)
    engine_presto = presto.connect('133.186.168.10')
    
    if len(select_ids) > 1:
        hql_ivt = """
        SELECT item_id, stock_id, stock_amount, collect_day, reg_dt
        FROM inventory_part
        WHERE item_part = {} AND
        month_part in {} and 
        item_id IN {}
        AND reg_dt > '{}'
        """.format(item_part, tuple([last_month, today.month]), select_ids, (today-datetime.timedelta(days=23)).strftime("%Y-%m-%d"))
    else:
        hql_ivt = """
        SELECT item_id, stock_id, stock_amount, collect_day, reg_dt
        FROM inventory_part
        WHERE item_part = {} AND
        month_part in {} and 
        item_id = {}
        AND reg_dt > '{}'
        """.format(item_part, tuple([last_month, today.month]), select_ids[0], (today-datetime.timedelta(days=23)).strftime("%Y-%m-%d"))
    
    return pd.read_sql_query(hql_ivt, engine_presto)


def pulling_items(target_item_ids, site_hive):
    ITEM_PART= np.array((target_item_ids // 10000) + 1)
    dic = {}

    for item_part, id in zip(ITEM_PART, target_item_ids):
        if not item_part in dic:
            dic[item_part] = [id]
        else:
            dic[item_part].append(id)

    today = datetime.datetime.today()
    last_month = (today - relativedelta(months=1)).month
    
    os.chdir("/app/dev/airflow/reposit")
    drt = "SC_{}_{}".format(site_hive, today.strftime("%m%d"))
    if not os.path.exists(drt): os.mkdir(drt)
    
    Parallel(n_jobs=-1)(joblib.delayed(retrieve_from_presto) (item_part, select_ids, today, last_month, drt) for item_part, select_ids in tqdm_notebook(dic.items()))
    return drt



def modify_1sec(df):
    df.sort_values("REG_DT", inplace=True)
    while True:
        df = df.assign(diff=df.REG_DT.diff().dt.total_seconds())
        if 1 not in df['diff'].values: break
        else: df.loc[df.REG_DT.isin(df.loc[df['diff']==1].REG_DT), 'REG_DT'] = df[df.REG_DT.isin(df.loc[df['diff']==1].REG_DT)].REG_DT - datetime.timedelta(seconds=1)
    return df
    
def calculate_r(x, n=7):
    x_c = n - x
    #0.5 for continuity correction
    r = -math.log( (x_c + 0.5) / (n + 0.5) )
    return r


def r_by_week(df, period):
    resampled = df.resample(period)['isChanged'].sum()
    return calculate_r(x=sum(resampled > 0)) * 1.5 #weight
    

def get_weighed_r_from_df(target, period='1D'):
    
    if len(target)==0: return -1
    elif target.isChanged.sum()==0: return 0

    r = target.groupby('week_dist').apply(r_by_week, '1D').reset_index()
    r.columns = ['WEEK', 'R_SCORE']
    weight = np.exp(-r['WEEK'])
    weighed_r = sum(weight*r['R_SCORE']) / sum(weight)
    
    return weighed_r
    
def assecing(items_df, R_drt):
    #preprocessing
    if len(items_df)==0: return 0
    items_df.columns = items_df.columns.str.upper()
    items_df = items_df.assign(REG_DT = pd.to_datetime(items_df['REG_DT']))
    
    #for get weighed r score
    max_reg = items_df.REG_DT.max()
    items_df = items_df.assign(week_dist = (max_reg-items_df.REG_DT).dt.days//7) 
    
    
    var_lst = [] #variable list
    
    for idx_item, group_item in items_df.groupby('ITEM_ID'):        
        groups = []
        group_item = modify_1sec(group_item) #1초차 교정
        
        #weather the most recent stock amount is 0 or not
        last_stock=[]
        for idx, group in group_item.groupby('STOCK_ID'):
            group = group.sort_values("REG_DT")
            group = group.assign(isChanged = np.where(np.append([0], np.diff(group.STOCK_AMOUNT.values)) !=0, 1, 0)) #whethere stock_amount changed or not
            groups.append(group)
            
            last_stock.append(group.iloc[-1].STOCK_AMOUNT)
        target = pd.concat(groups)
        
        #for RESAMPLE(used in get r score function)
        target = target.assign(COLLECT_DAY = pd.to_datetime(target.COLLECT_DAY))
        target = target.set_index('COLLECT_DAY', drop=False)
        
        #get features
        crawled = target.REG_DT.nunique() #the number of crawl time
        changed = target.groupby('REG_DT').isChanged.max().sum() #the number of times which stock_amount is changed when crawled
        period = (target.REG_DT.max() - group.REG_DT.min()).days #the period we've crawled
        changed_day = target.groupby("COLLECT_DAY", as_index=True).isChanged.max().sum() #change by day #the number of days which stock_amount is changed more than one
        last_stock = sum(last_stock)==0 #weather the most recent stock amount is 0 or not
        n_stock = target.STOCK_ID.nunique() #the number of options the given item has
        var_lst.append((idx_item, crawled, changed, changed_day, period, last_stock, n_stock, get_weighed_r_from_df(target))) #aggregate features
        
    
    pd.DataFrame(var_lst, columns = ['ITEM_ID', 'CRAWL', 'CHANGE', 'CHANGED_DAY', 'PERIOD', 'LAST_STOCK_IS_ZERO', 'N_STOCK', 'R_SCORE']).to_parquet("{}/{}".format(R_drt, parq.split("/")[1]))
    
    return len(var_lst)

