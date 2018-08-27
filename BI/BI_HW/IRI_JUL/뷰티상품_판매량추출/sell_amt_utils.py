from __future__ import print_function
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.mysql_operator import MySqlOperator
from airflow.models import DAG
from sqlalchemy import create_engine
import feather
import json
from datetime import datetime, timedelta
# from airflow.hooks.mysql_hook import MySqlHook
from airflow.hooks import MySqlHook
import time
import math
import shutil

from pytz import timezone
import logging

import pandas as pd
import numpy as np
from sklearn import preprocessing
import numpy as np
import urllib
from scipy import stats
import sys
from multiprocessing import Queue
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
import logging
# import cPickle as pickle
import pickle
import os
import warnings
import glob
from sqlalchemy import event
from sqlalchemy import exc
from time import gmtime, strftime
from datetime import datetime
import itertools
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from fancyimpute import KNN

wspider_temp_engine = create_engine("mysql://eums:eums00!q@115.90.182.250:11000/wspider_temp", pool_size=20, pool_recycle=3600,
                       connect_args={'connect_timeout': 1000000})
wspider_engine = create_engine("mysql://wspider:wspider00!q@192.168.0.36:3306/wspider", pool_size=20, pool_recycle=3600,
                   connect_args={'connect_timeout': 1000000})

logger = logging.getLogger()

def impute_data(target):
    # cluster inventory data points



    n_cluster, label = get_label_from_dbscan(target, eps=0.15, min_samples=3)
    target = target.assign(label=label)
    target = target[['STOCK_AMOUNT', 'label', 'REG_DT']]
    labels = target.label.unique()

    # resample to a daily scale
    target = target.set_index('REG_DT')
    target = target.resample('1D').first()

    # placeholding
    target['STOCK_AMOUNT_imputed'] = target['STOCK_AMOUNT']

    # interpolate data points based on cluster group
    for label in labels:
        idx = np.where(target.label.values == label)[0]
        if len(idx) == 0:
            continue
        start_v = min(idx)
        end_v = max(idx)
        target.loc[start_v:end_v + 1, 'STOCK_AMOUNT_imputed'] = target['STOCK_AMOUNT'][start_v:end_v + 1].interpolate(
            method='from_derivatives')

    # interpolate data points based on global data points
    target['STOCK_AMOUNT_imputed'] = target['STOCK_AMOUNT'].interpolate(method='from_derivatives')

    # round STOCK_AMOUNT_imputed to make it cleaner
    target['STOCK_AMOUNT_imputed'] = target.STOCK_AMOUNT_imputed.round()

    # calculate sell amount
    target['sell'] = np.append([0], np.negative(np.diff(target.STOCK_AMOUNT_imputed)))
    target.loc[target['sell'].values < 0, 'sell'] = np.nan
    target.sell.astype(float)

    # calculate z-score for thresholding
    target['zscore'] = np.abs(target.sell - target.sell.mean() / max(0.0001, target.sell.std()))

    # get rid of outliers
    target.loc[target['zscore'] > 4, 'sell'] = np.nan

    # prepare matrix for data imputation using KNN based on dayofweek
    target['weekday_name'] = target.index.dayofweek
    X_incomplete = target[['sell', 'weekday_name']].values

    # run KNN to calculate sell_impute (imputed version of sell amount)
    try:
        X_filled_knn = KNN(k=1, verbose=False).complete(X_incomplete)
        target['sell_impute'] = X_filled_knn[:, 0]
    except:
        target['sell_impute'] = target['sell']

    # placeholding
    target['STOCK_AMOUNT_imputed_trimed'] = target['STOCK_AMOUNT_imputed']

    # get rid of jumpbs
    cond = np.append([0], np.negative(np.diff(target.STOCK_AMOUNT_imputed))) < 0
    target.loc[cond, 'STOCK_AMOUNT_imputed_trimed'] = np.nan

    return target

def get_sell_amount_by_item_id(df, add_sell_amount=False):
    collect_day = df.COLLECT_DAY.values[0]
    reg_id = df.REG_ID.values[0]

    imputed_df_lst = []
    for stock_id, group_df in list(df.groupby('STOCK_ID')):
        imputed_df = impute_data(group_df)[['sell_impute', 'STOCK_AMOUNT', 'STOCK_AMOUNT_imputed_trimed']]
        imputed_df['STOCK_ID'] = stock_id
        imputed_df_lst.append(imputed_df)



    imputed_df = pd.concat(imputed_df_lst)
    imputed_df.columns = ['SELL_AMOUNT', 'STOCK_AMOUNT', 'REVISE_STOCK_AMOUNT', 'STOCK_ID']
    imputed_df['ITEM_ID'] = df.ITEM_ID.values[0]
    imputed_df['REG_ID'] = reg_id
    imputed_df['UPT_DT'] = pd.to_datetime(datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S"))
    imputed_df['COLLECT_DAY'] = collect_day
    imputed_df['UPT_ID'] = 'FILTER ALGO'



    return imputed_df


def get_label_from_dbscan(df, eps=0.2, min_samples=3, outlier=True):
    df = df.fillna(-1)
    outlier = True

    date = df.index
    df['INDEX'] = np.arange(3, len(df.STOCK_AMOUNT) + 3)
    Z = df[['STOCK_AMOUNT', 'INDEX']].values
    Z = np.vstack((Z, [[0, 2], [500, 1]]))
    Z = Z.astype(float)

    scaler = preprocessing.MinMaxScaler(feature_range=(0, 100))
    Z[:, 0] = scaler.fit_transform(Z[:, 0].reshape(-1, 1))[:, 0]
    X = StandardScaler().fit_transform(Z)
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    return (n_clusters_, labels[:-2])

def get_feature_engineered_bundle(df):
    def get_arr_in_cluster(df):

        empty_lst = []
        for name, group in df.groupby('label')['STOCK_AMOUNT']:
            result_lst = np.sort(np.diff(group))[1:-1]
            empty_lst = np.append(empty_lst, result_lst)
        arr_in_cluster = -empty_lst[empty_lst < 0]
        return arr_in_cluster

    # The number of unique stock_id

    df = df.set_index("REG_DT")
    unique_stock_ids = df.STOCK_ID.unique()
    n_unique_stock_id = len(unique_stock_ids)

    # select a single stock_id
    tmp2 = list(df.groupby('STOCK_ID'))[0][1]

    # The ratio of NA
    tmp3 = tmp2.resample('1D').first()

    # The number of days
    n_days = len(tmp3.ID)

    if n_days <= 1:
        return

    null_arr = pd.isnull(tmp3.ID).values
    ratio_of_na = sum(null_arr) / float(n_days)

    consecutive_lst = [sum(1 for _ in group) for key, group in itertools.groupby(null_arr) if key]

    # The max value of consecutive NAs
    max_consecutive_na = max([0] + consecutive_lst)

    # The instances of consecutive NAs
    n_consecutive_na = len(consecutive_lst)

    # Define a stock array
    stock_arr = tmp3.STOCK_AMOUNT.values

    # The medain
    median_v = np.nanmedian(stock_arr)

    # Std
    std_v = np.nanstd(stock_arr)

    # max, min
    max_v = np.nanmax(stock_arr)
    min_v = np.nanmin(stock_arr)

    # The range between max and min
    range_v = max_v - min_v

    stock_na_removed = stock_arr[~np.isnan(stock_arr)]

    consecutive_same_lst = [sum(1 for _ in group) for key, group in itertools.groupby(stock_na_removed) if key]

    if len(consecutive_same_lst) == 0:
        ratio_same_value = 0
    else:
        ratio_same_value = max(consecutive_same_lst) / float(n_days)

    n_jumps = sum(np.diff(stock_na_removed) > 0)
    max_drop = -min(np.diff(stock_na_removed))

    tmp3['STOCK_AMOUNT'] = tmp3.STOCK_AMOUNT.replace(np.nan, -1)
    n_cluster, label = get_label_from_dbscan(tmp3)

    tmp3 = tmp3.assign(label=label)

    arr_in_cluster = get_arr_in_cluster(tmp3)

    if len(arr_in_cluster) > 0:

        mean_in_cluster = np.nanmean(arr_in_cluster)
        std_in_cluster = np.nanstd(arr_in_cluster)
    else:
        mean_in_cluster = 0
        std_in_cluster = 0

    bundle = {
        'item_id': df.ITEM_ID.values[0],
        'stock_id': df.ITEM_ID.values[0],
        'n_unique_stock_id': n_unique_stock_id,
        'n_days': n_days,
        'ratio_of_na': ratio_of_na,
        'max_consecutive_na': max_consecutive_na,
        'n_consecutive_na': n_consecutive_na,
        'median_v': median_v,
        'std_v': std_v,
        'max_v': max_v,
        'ratio_drop': max_drop / max(float(max_v), 0.00001),
        'min_v': min_v,
        'range_v': range_v,
        'ratio_same_value': ratio_same_value,
        'n_jumps': n_jumps,
        'max_drop': max_drop,
        'n_cluster': n_cluster,
        'mean_in_cluster': mean_in_cluster,
        'std_in_cluster': std_in_cluster

    }

    return bundle

def get_filtered_fg_df(feature_engineered_df, brand=False):
    static_item_ids = feature_engineered_df.item_id[(feature_engineered_df.std_in_cluster == 0.0)].values
    data_df_cleaned = feature_engineered_df[feature_engineered_df.mean_in_cluster.notnull()]

    purified_df = data_df_cleaned[(data_df_cleaned.ratio_drop < 0.3)
                                  & (data_df_cleaned.ratio_same_value < 0.3)
                                  & (data_df_cleaned.n_jumps <= 3)
                                  & (data_df_cleaned.n_days >= 3)
                                  & (data_df_cleaned.std_in_cluster > 0.2)
                                  & (data_df_cleaned.std_in_cluster < 4)
                                  & (data_df_cleaned.ratio_of_na < 0.5)
                                  & (data_df_cleaned.n_unique_stock_id < 50)]
    return purified_df, static_item_ids


def insert_extracted_feature(wspider_temp_engine, extracted_feature_df):
    extracted_feature_df = extracted_feature_df.where((pd.notnull(extracted_feature_df)), None)
    query = """REPLACE MWS_COLT_ITEM_EXTRACTED_FEATURE %s VALUES %s """ % (
    tuple(extracted_feature_df.columns), tuple(['%s' for _ in range(len(extracted_feature_df.columns))]))
    query = query.replace("'", "")
    wspider_temp_engine.execute(query, [tuple(x) for x in extracted_feature_df.values])

def get_chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def insert_sell_amt(engine, batch_sell_amt, development=False):


    batch_sell_amt['UPT_DT'] = batch_sell_amt['UPT_DT'].astype(str)
    batch_sell_amt['REG_DT'] = batch_sell_amt['REG_DT'].astype(str)
    batch_sell_amt['COLLECT_DAY'] = batch_sell_amt['COLLECT_DAY'].astype(str)
    batch_sell_amt = batch_sell_amt.where((pd.notnull(batch_sell_amt)), None)
    col_names = ['SELL_AMOUNT', 'REVISE_STOCK_AMOUNT', 'STOCK_AMOUNT', 'STOCK_ID', 'ITEM_ID', 'COLLECT_DAY', 'REG_ID', 'REG_DT', 'UPT_DT', 'UPT_ID']

    if development:
        query = "INSERT INTO wspider_temp.MWS_COLT_ITEM_SELL_AMT_DEV" + str(tuple(col_names)) + " VALUES %s ON DUPLICATE KEY UPDATE SELL_AMOUNT=%s, REVISE_STOCK_AMOUNT=%s, STOCK_AMOUNT=%s"
    else:

        query = "INSERT INTO wspider.MWS_COLT_ITEM_SELL_AMT" + str(tuple(col_names)) + " VALUES %s ON DUPLICATE KEY UPDATE SELL_AMOUNT=%s, REVISE_STOCK_AMOUNT=%s, STOCK_AMOUNT=%s"
    query = query.replace("'", "")
    values = [(tuple(row), row[0], row[1], row[2]) for row in batch_sell_amt[col_names].values]

    total_n_rows = len(values)

    n_items = 10000
    # list(get_chunks(values, n_items))
    chunks = get_chunks(values, n_items)
    i = 0
    for chunk in chunks:
        print((i * n_items * 100 ) / float(total_n_rows))
        engine.dispose()
        engine.execute(query, chunk)
        i += 1

def insert_sell_amt_old(engine, sell_amt_df, development):

    print(sell_amt_df.head(3))

    print("-----------------------------------")

    sell_amt_df['UPT_DT'] = sell_amt_df['UPT_DT'].astype(str)
    sell_amt_df['REG_DT'] = sell_amt_df['REG_DT'].astype(str)
    sell_amt_df['COLLECT_DAY'] = sell_amt_df['COLLECT_DAY'].astype(str)
    sell_amt_df = sell_amt_df.where((pd.notnull(sell_amt_df)), None)
    col_names = sell_amt_df.columns.values

    # print(col_names)
    col_names = str(tuple([str(elem) for elem in col_names]))
    # #
    # # col_names = sell_amt_df.columns.values
    # # col_names = [str(elem) for elem in col_names]
    # sell_amt_df.columns = col_names

    # print(sell_amt_df)

    print("-----------------------------------")

    # print(sell_amt_df.head(3))

    # sell_amt_df = sell_amt_df.where((pd.notnull(sell_amt_df)), None)

    sell_amt_df_splits = np.split(sell_amt_df, [50], axis=0)

    i = 0

    for sell_amt_df_split in sell_amt_df_splits:
        print(i)
        engine.dispose()
        # connection = engine.connect()
        if development:

            query = """REPLACE INTO MWS_COLT_ITEM_SELL_AMT_DEV %s VALUES %s """ % (
                col_names, tuple(['%s' for _ in range(len(sell_amt_df_split.columns))]))
            query = query.replace("'", "")
            engine.execute(query, [tuple(x) for x in sell_amt_df_split.values])
        else:
            query = """REPLACE INTO MWS_COLT_ITEM_SELL_AMT %s VALUES %s """ % (
                col_names, tuple(['%s' for _ in range(len(sell_amt_df_split.columns))]))
            query = query.replace("'", "")
            print("////////////////////")
            print(query)
            print("////////////////////")

            # print(sell_amt_df_split.values)
            engine.execute(query, [tuple(x) for x in sell_amt_df_split.values])

        i += 1
    # query2 = """REPLACE INTO MWS_COLT_ITEM_SELL_AMT %s VALUES %s """ % (
    # tuple(sell_amt_df.columns), tuple(['%s' for _ in range(len(sell_amt_df.columns))]))
    # query2 = query2.replace("'", "")
    # wspider_engine.execute(query2, [tuple(x) for x in sell_amt_df.values])

def apply_feature_engineering(wspider_engine, wspider_temp_engine, dataset):

    site_name = dataset['SITE_NAME']
    item_ids = str(tuple([item_id for item_id in dataset['ITEM_IDS']]))
    sql = "SELECT ID, ITEM_ID, STOCK_ID, STOCK_AMOUNT, COLLECT_DAY, REG_ID, REG_DT FROM wspider.MWS_COLT_ITEM_IVT WHERE ITEM_ID IN %s" % item_ids
    batch = pd.read_sql_query(sql, wspider_engine)

    # extract features by stock id
    result_lst = []
    for idx, group in batch.groupby('ITEM_ID'):
        result_lst.append(get_feature_engineered_bundle(group))

    # clean up extracted feature df
    extracted_feature_df = pd.DataFrame([result for result in result_lst if result != None])

    if site_name in ['DESCENTE', 'GSSHOP', 'nbkorea', 'NIKE']:
        try:
            extracted_feature_df['condition_clean'] = 2
        except:
            return

    else:
        try:
            # filter dataframe based on extraction criteria
            filtered_df, static_item_ids = get_filtered_fg_df(extracted_feature_df)

            # filtered df
            cleaned_item_ids = filtered_df.item_id.values
            cleaned_df = batch[batch['ITEM_ID'].isin(cleaned_item_ids)]

            # label extracted feature df
            extracted_feature_df['condition_clean'] = 0
            extracted_feature_df.loc[extracted_feature_df.item_id.isin(cleaned_item_ids), 'condition_clean'] = 1
            extracted_feature_df.loc[extracted_feature_df.item_id.isin(static_item_ids), 'condition_clean'] = 2


        except:
            return

    extracted_feature_df = extracted_feature_df.where((pd.notnull(extracted_feature_df)), None)
    insert_extracted_feature(wspider_temp_engine, extracted_feature_df)


def apply_model(partition, batch):

    # sql = "SELECT ID, ITEM_ID, STOCK_ID, STOCK_AMOUNT, COLLECT_DAY, REG_ID, REG_DT FROM wspider.MWS_COLT_ITEM_IVT WHERE ITEM_ID IN %s" % item_ids
    # batch = pd.read_sql_query(sql, wspider_engine)



    cond = pd.notnull(batch['STOCK_ID']) & (batch['STOCK_ID'] != '') & pd.notnull(batch['ITEM_ID'])

    batch = batch.loc[cond]

    df_lst = []
    cleaned_df = batch.sort_values(by=['ITEM_ID', 'STOCK_ID', 'REG_DT'])

    batch_len = len(batch.ITEM_ID.unique())

    i = 0
    logger.info("Let's begin!!")
    for idx, group in cleaned_df.groupby('ITEM_ID'):
        try:
            df_lst.append(get_sell_amount_by_item_id(group))

        except:
            continue
        i += 1

        if i % 50 == 0:
            logger.info(str(i * 100/ float(batch_len)) + "% done")

    if len(df_lst) > 0:
        result = pd.concat(df_lst)



        result['COLLECT_DAY'] = result.index
        result['REG_DT'] = result.index
        result = result.where((pd.notnull(result)), None)
        result = result.reset_index(drop=True)

        write_to_feather(partition, result, processed=True)
        # insert_sell_amt(wspider_engine, wspider_temp_engine, result)

def write_to_feather(partition, data, processed=True, meta=False):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    if meta:
        print('1')
        filename = "item_ids.feather"
        complete_filename = os.path.join(path, "tmp_feathers/meta", filename)
        print('2')
        # data.to_feather(complete_filename)
        # feather.write_dataframe(data, complete_filename)
        data.to_pickle(complete_filename)
        print('3')
        return True

    if processed:

        filename = "processed_%s.feather" % str(partition)
        complete_filename = os.path.join(path, "tmp_feathers/processed", filename)
    else:
        filename = "raw_%s.feather" % str(partition)
        complete_filename = os.path.join(path, "tmp_feathers/raw", filename)

    data.to_feather(complete_filename)

def remove_meta_file():

    print('remove_meta_file!!!!!!!!!!')
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    complete_filename = os.path.join(path, "tmp_feathers/meta", "item_ids.feather")


    if os.path.isfile(complete_filename):
        try:
            if os.path.isfile(complete_filename):
                os.unlink(complete_filename)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def read_feather(partition, processed=True, meta=False):

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if meta:
        filename = "item_ids.feather"
        complete_filename = os.path.join(path, "tmp_feathers/meta", filename)
        return pd.read_pickle(complete_filename)


    if processed:
        filename = "processed_%s.feather" % str(partition)
        complete_filename = os.path.join(path, "tmp_feathers/processed", filename)
    else:
        filename = "raw_%s.feather" % str(partition)
        complete_filename = os.path.join(path, "tmp_feathers/raw", filename)
    return pd.read_feather(complete_filename)


def apply_model_old(wspider_engine, wspider_temp_engine, dataset):
    site_name = dataset['SITE_NAME']
    item_ids = dataset['ITEM_IDS']

    if site_name not in ['DESCENTE', 'GSSHOP', 'nbkorea', 'NIKE']:
        sql = "SELECT item_id FROM wspider_temp.MWS_COLT_ITEM_EXTRACTED_FEATURE WHERE condition_clean = 0"

        result = pd.read_sql_query(sql, wspider_temp_engine)
        filter_set = set(result.item_id.values)

        item_ids = np.array([item for item in item_ids if item not in filter_set])

    item_ids = str(tuple([item_id for item_id in item_ids]))
    sql = "SELECT ID, ITEM_ID, STOCK_ID, STOCK_AMOUNT, COLLECT_DAY, REG_ID, REG_DT FROM wspider.MWS_COLT_ITEM_IVT WHERE ITEM_ID IN %s" % item_ids
    batch = pd.read_sql_query(sql, wspider_engine)

    cond = pd.notnull(batch['STOCK_ID']) & (batch['STOCK_ID'] != '') & pd.notnull(batch['ITEM_ID'])

    batch = batch.loc[cond]

    df_lst = []
    cleaned_df = batch.sort_values(by=['ITEM_ID', 'STOCK_ID', 'REG_DT'])

    for idx, group in cleaned_df.groupby('ITEM_ID'):
        try:
            df_lst.append(get_sell_amount_by_item_id(group))

        except:
            continue

    if len(df_lst) > 0:
        result = pd.concat(df_lst)
        result['COLLECT_DAY'] = result.index
        result['REG_DT'] = result.index
        result = result.where((pd.notnull(result)), None)

        insert_sell_amt(wspider_engine, wspider_temp_engine, result)