from sqlalchemy import create_engine
import pandas as pd
from pyhive import presto
import os
import datetime
import time

import logging

import time
import pymysql

logger = logging.getLogger()

site_list = ['DESCENTE', 'GSSHOP', 'HMALL', 'NIKE', 'OLIVEYOUNG', 'adidas', 'lotte.com', 'nbkorea']


def process(df, time_str, week_part):
    for site in site_list:
        calc_x_time_y_amount(df, site, time_str, week_part)

#시간별 크롤량 계산하는 함수
def calc_x_time_y_amount(df, site_str, time_str, week_part):
    try :  
        site_df = df[df['site']== site_str]
        site_df = site_df.resample(time_str, on='my_time').sum()
        site_df = site_df['count'].reset_index()
        site_df.columns = ['time', 'count']
        
        site_to_db(site_df, site_str, week_part, time_str)
    except:
        logger.info('error in calc_x_time_y_amount OR site_to_db : Probably an error due to nothing new data')
        return False
    return True



# db에 저장
def site_to_db(site_df, site_name, week_part, time_str):
    epopcon_engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.118:3306/eums-poi", pool_size=20, pool_recycle=3600,
                           connect_args={'connect_timeout': 1000000})

    for i in range(0, len(site_df)):
        query = """
        INSERT INTO CRAWLING_AMOUNT
        SET TIME = '{}', SITE = '{}', AMOUNT = '{}',REG_DT = '{}', UPT_DT = '{}', MODIFIER = '{}', STATUS = '{}'
        """.format(site_df.iloc[i]['time'], site_name, site_df.iloc[i]['count'],datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'KOOKMIN', 1)

    
        logger.info(query)
        with epopcon_engine.connect() as con:
            con.execute(query)

# 몇번째 주인지를 계산하는 함수. Presto 에서 Week_part 로 접근하기 위해서 필요함
def calc_nth_weeks(day):
    return (day.isocalendar()[1] + 1 ) if (day.isocalendar()[2] == 7) else (day.isocalendar()[1])


# 메인함수. DAG 를 쓰기 위해 main 부분을 함수로 구현
def my_main():

    epopcon_engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.118:3306/eums-poi", pool_size=20, pool_recycle=3600,
                           connect_args={'connect_timeout': 1000000})

    query = """
        SELECT MAX(REG_DT) FROM CRAWLING_AMOUNT
        """
    max_day_df = pd.read_sql_query(query, epopcon_engine)
    last_line = max_day_df['MAX(REG_DT)'][0]

    
    last_line_2 = last_line.split(' ')
    last_line_list = last_line_2[0].split('-')
    final_upt_date = datetime.date(int(last_line_list[0]), int(last_line_list[1]), int(last_line_list[2]))

    now = datetime.datetime.now()
    logger.info(now)
    

    start_week_part = calc_nth_weeks(final_upt_date)
    end_week_part = calc_nth_weeks(now)

    logger.info('week part')
    logger.info(start_week_part)
    logger.info('end week part')
    logger.info(end_week_part)

    engine_presto = presto.connect('133.186.168.10')
    
    last_line = last_line.split('\n')
    last_line = str(last_line[0])

    
    start_date = datetime.datetime.strptime(last_line, '%Y-%m-%d %H:%M:%S')
    
    end_date = now
    


    for week_part in range(start_week_part, end_week_part+1):    
        hql_item_ids = """
            SELECT *
            from item_part
            where week_part = {} 
            """.format(week_part)


        df_item_part = pd.read_sql_query(hql_item_ids, engine_presto)

        df_item_part['my_time'] = pd.to_datetime(df_item_part['upt_dt'])

        df_item_part = df_item_part[(df_item_part['my_time'] >= start_date) & (df_item_part['my_time'] <= end_date)]
        
        df = df_item_part.groupby(['site_name', 'my_time'])['id'].count().reset_index()
        df.columns = ['site', 'my_time', 'count']


        logger.info(df)

        process(df, '15T', week_part)
    









