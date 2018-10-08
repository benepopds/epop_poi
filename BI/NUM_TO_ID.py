#This function transforms ITEM_NUM into ITEM_ID using MWS_COLT_ITEM table
#It supposes that you are using RDBMS, so transforms only ten items for each iteration

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://wspider:wspider00!q@192.168.0.36:3306/wspider", pool_size=20, pool_recycle=3600, connect_args={'connect_timeout': 1000000})


def num_to_id(df):
    chunk_size = int(len(df)/10)
    ids = []
    for i in np.array_split(df.ITEM_NUM.values, chunk_size):
        query = """
        select ID
        from MWS_COLT_ITEM 
        where ITEM_NUM in {}
        """.format(tuple(i))
        ids.append(pd.read_sql_query(query,engine)["ID"].values)
    return np.concatenate(ids).ravel()
