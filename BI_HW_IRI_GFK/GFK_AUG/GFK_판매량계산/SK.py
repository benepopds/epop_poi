# Perform imports here:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pytz import timezone
from sqlalchemy import create_engine
import math
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN


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
    #target.loc[target['zscore'] > 4, 'sell'] = np.nan

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
    #reg_id = df.REG_ID.values[0]

    imputed_df_lst = []
    for stock_id, group_df in list(df.groupby('STOCK_ID')):
        imputed_df = impute_data(group_df)[['sell_impute', 'STOCK_AMOUNT', 'STOCK_AMOUNT_imputed_trimed']]
        imputed_df['STOCK_ID'] = stock_id
        imputed_df_lst.append(imputed_df)



    imputed_df = pd.concat(imputed_df_lst)
    imputed_df.columns = ['SELL_AMOUNT', 'STOCK_AMOUNT', 'REVISE_STOCK_AMOUNT', 'STOCK_ID']
    imputed_df['ITEM_ID'] = df.ITEM_ID.values[0]
    #imputed_df['REG_ID'] = reg_id
    imputed_df['UPT_DT'] = pd.to_datetime(datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S"))
    imputed_df['COLLECT_DAY'] = collect_day
    imputed_df['UPT_ID'] = 'FILTER ALGO'

    return imputed_df

def apply_model(batch): #2018-08-03 수정본 사용
    
    # sql = "SELECT ID, ITEM_ID, STOCK_ID, STOCK_AMOUNT, COLLECT_DAY, REG_ID, REG_DT FROM wspider.MWS_COLT_ITEM_IVT WHERE ITEM_ID IN %s" % item_ids
    # batch = pd.read_sql_query(sql, wspider_engine)

    cond = pd.notnull(batch['STOCK_ID']) & (batch['STOCK_ID'] != '') & pd.notnull(batch['ITEM_ID'])

    batch = batch.loc[cond]

    df_lst = []
    cleaned_df = batch.sort_values(by=['ITEM_ID', 'STOCK_ID', 'REG_DT'])

    batch_len = len(batch.ITEM_ID.unique())
    
    
    i = 0
    #print("Let's begin!!")
    for idx, group in cleaned_df.groupby('ITEM_ID'):
        try:
            df_lst.append(get_sell_amount_by_item_id(group))
        except:
            continue
        i += 1

        #if i % 50 == 0:
        #    print(str(i * 100/ float(batch_len)) + "% done")
    
    if len(df_lst) > 0:
        result = pd.concat(df_lst)



        result['COLLECT_DAY'] = result.index
        result['REG_DT'] = result.index
        result = result.where((pd.notnull(result)), None)
        result = result.reset_index(drop=True)
#         result.to_parquet("GSS/{}.pq".format(k))
        #write_to_feather(partition, result, processed=True)
        # insert_sell_amt(wspider_engine, wspider_temp_engine, result)
#         print("{}%% is done!".format(round(k*100/chunk, 1))) 0803 수정
        return result
    else:
        return "ERROR"
