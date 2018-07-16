import pandas as pd
import numpy as np
import datetime
from sqlalchemy import create_engine
import pymysql, pandas as pd
pymysql.install_as_MySQLdb()
import MySQLdb
import os
import re

engine = create_engine("mysql://eums:eums00!q@192.168.0.118:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

query = """
        SELECT *
        FROM TEMP0001
        WHERE STATE=0
        """

db_df = pd.read_sql_query(query, engine)
uni_df = pd.read_csv("result_ngram_se/unigram.txt", delimiter=' ', header=None, names=['name', 'count'])
bi_df = pd.read_csv("result_ngram_se/bigram.txt", delimiter=' ', header=None, names=['name1','name2', 'count'])
tri_df = pd.read_csv("result_ngram_se/trigram.txt", delimiter=' ', header=None, names=['name1','name2','name3', 'count'])

uni_pro_df = pd.read_csv("result_ngram_se/unigram_probability.txt", delimiter=' ', header=None, names=['name', 'pro'])
bi_pro_df = pd.read_csv("result_ngram_se/bigram_probability.txt", delimiter = ' ', header=None, names=['name1', 'name2', 'pro' ])
tri_pro_df = pd.read_csv("result_ngram_se/trigram_probability.txt", delimiter = ' ', header=None, names=['name1','name2', 'name3','pro' ])


r = re.compile("[0-9\-]")



for index, row in db_df.iterrows():
    exit_flag = False
    row_str = db_df['ADDR'][index]


    row_str = str(row_str).replace('[','').replace(']','').replace('(','').replace(')','')

    row_str = re.sub('[-=.#/?:$}]','',row_str)

    print('row_str')
    print(row_str)
    if len(row_str) < 2:
        break
    #강서구 내발산동 703
    row_list = row_str.split(' ')


    tmp_index_save=0
    del_result_str = ""
    index = 0
    for row_list_data in row_list:
        if r.search(row_list_data) == None:
            del_result_str += row_list_data +" "
        else:
            tmp_index_save = index
        index +=1
    del_result_str = del_result_str[:len(del_result_str) -1]
    print('del_result_str')
    print(del_result_str)
    #강서구 내발산동

    tmp_save_str = row_list[tmp_index_save]
    print('tmp_save_str')
    print(tmp_save_str)
    #703
    tmp_save_str_before = row_list[tmp_index_save-1]
    print('tmp_save_str_before')
    print(tmp_save_str_before)
    #내발산동

    del row_list[tmp_index_save]
    row_list.reverse()

    reverse_str = " ".join(row_list)

    ## 맨 뒤에 띄어쓰기 사라젔는지 확인
    if len(reverse_str) >0 and reverse_str[-1] == " ":
        reverse_str = reverse_str[:-1]

    reverse_list = reverse_str.split(' ')
    print('reverse_list')
    print(reverse_list)
    #['내발산동', '강서구']



    tmp_result_str = str(reverse_list[0])
    tmp_result_str += " "
    print('tmp_result_str')
    print(tmp_result_str)
    #내발산동


    index = 0
    save_before_reverse_list_small = ''
    for reverse_list_small in reverse_list:
        if exit_flag:
            tmp_result_str = reverse_str
            break
        if index ==0 :
            try:
                ex_value = bi_pro_df[bi_pro_df['name1']==reverse_list_small].iloc[0]['name2']
            except:
                exit_flag = True
        else :
            try:
                ex_value = tri_pro_df[ (tri_pro_df['name1'] == save_before_reverse_list_small) & (tri_pro_df['name2'] == reverse_list_small )].iloc[0]['name3']
            except:
                exit_flag = True


        tmp_result_str += str(ex_value)
        if index != len(reverse_list)-1:
            tmp_result_str += " "

        index +=1
        save_before_reverse_list_small = reverse_list_small


    tmp_result_list = tmp_result_str.split(' ')
    tmp_result_list.reverse()
    print('tmp_result_list')
    print(tmp_result_list)
    #['서울특별시', '강서구', '내발산동']

    real_result_str = ""

    for tmp_result_item in tmp_result_list:
        if tmp_result_item != tmp_save_str_before:
            real_result_str +=tmp_result_item
            real_result_str += ' '
        else:
            real_result_str += tmp_result_item
            real_result_str += ' '
            real_result_str += tmp_save_str
            real_result_str += ' '

    print('real_result_str')
    print(real_result_str)
    #서울특별시 강서구 내발산동 703
    real_result_str = real_result_str.replace("^", "")
    real_result_str = real_result_str.replace("  ", "")
    print('real_result_str - modify')
    print(real_result_str)
    #서울특별시 강서구 내발산동 703
    print('#')
    try:
        if real_result_str[0] == " ":
            real_result_str = real_result_str.replace(" ","",1)
    except:
        real_result_str = real_result_str



    print(real_result_str)
    print()
    query = """
        INSERT INTO ngram_test
        SET addr_before='{}', addr_after='{}'
        """.format(row_str,real_result_str)
    print(query)
    with engine.connect() as con:
        con.execute(query)

    print('###############################')
