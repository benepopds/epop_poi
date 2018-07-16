import pandas as pd
import numpy as np
import datetime
from sqlalchemy import create_engine
import pymysql, pandas as pd
pymysql.install_as_MySQLdb()
import MySQLdb
import os
import re

# engine = create_engine("mysql://eums:eums00!q@192.168.0.50:3306/eums?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )
#
# query = """
#         SELECT ADDR
#         FROM MEUMS_COMPANY
#         """

engine = create_engine("mysql://eums:eums00!q@192.168.0.118:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

query = """
        SELECT ADDR
        FROM TEMP0001
        """

print(query)
addr_df = pd.read_sql_query(query, engine)

f = open("addr_text_se.txt", 'a')
r = re.compile("[0-9\-]")

for index, row in addr_df.iterrows():
    row_str = "^ "
    row_str += row['ADDR']
    row_str += ' $'
    row_list = row_str.split(' ')
    for a in row_list:
        if r.search(a) == None:
            f.write(a + " ")
f.close()
