from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from pyhive import presto
import os
from operator import itemgetter, attrgetter, methodcaller
from joblib import Parallel
import joblib
from pymongo import MongoClient
import glob
from dask import delayed
import datetime
import datetime as dt
import time
from pytz import timezone
import time
import pymysql
import plotly.offline as pyo
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from pandas import Series, DataFrame



app = dash.Dash()

all_options = {
    'item_part' : ['adidas', 'DESCENTE', 'GSSHOP', 'HMALL', 'lotte.com', 'nbkorea', 'NIKE', 'OLIVEYOUNG'],
}

marker1 = dict(color='rgba(255,0,0,.7)')
marker2 = dict(color='rgba(0,0,0,.9)')
marker3 = dict(color='rgba(0,0,0,.6)')

app.layout = html.Div([
        html.Div([
            dcc.Dropdown(
                id='column_type',
                options= [ {'label' : k , 'value' : k} for k in all_options.keys() ] ,
                value='item_part',
            ),
            dcc.Dropdown(
                id='company_type',
                value = 'adidas'

            ),
            html.Div([
                dcc.Input(
                    id='startdate_input',
                    type='Date',
                    value=dt.date.today()
                ),
                dcc.Input(
                    id='enddate_input',
                    type='Date',
                    value=dt.date.today()
                ),
            ]),

        ],
        style={'width': 200, 'height':200}
        ),
        html.Button(id='submit_button', n_clicks=0, children='Submit', style={'fontSize':20, 'height':50}),

    dcc.Graph(id='feature-graphic'),
    dcc.Markdown(id = 'content_text', containerProps={'fontSize':200}),

    
   
])

@app.callback(
    Output('company_type', 'options'),
    [Input('column_type', 'value')]
)

def set_company_type(select_column):
    return [ {'label' : i , 'value' : i} for i in all_options[select_column]]

@app.callback(
    Output('company_type', 'value'),
    [Input('company_type', 'options')]
)
def set_company_value(avail_options):
    return avail_options[0]['value']


def date_str_to_datetime(date):
    date_list = date.split('-')
    return datetime.datetime(int(date_list[0]),int(date_list[1]),int(date_list[2]))


def draw_graph_item_part(n_clicks,startdate_input,enddate_input, company_type, time):
    start_day = date_str_to_datetime(startdate_input)    
    end_day = date_str_to_datetime(enddate_input)
    
    end_tmp = end_day.strftime("%Y-%m-%d")
    end_tmp = str(end_tmp) + " 23:59:59"

    start_date = start_day
    end_date = datetime.datetime.strptime(str(end_tmp) ,'%Y-%m-%d %H:%M:%S')


    epopcon_engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.118:3306/eums-poi", pool_size=20, pool_recycle=3600,
                           connect_args={'connect_timeout': 1000000})
    query = """
    SELECT TIME, SITE, AMOUNT
    FROM CRAWLING_AMOUNT
    WHERE TIME BETWEEN '{}' and '{}' and SITE = '{}'
    """.format(start_date, end_date, company_type)

    result_df = pd.read_sql_query(query, epopcon_engine)

    print(result_df)

    total_crawl_amount = result_df['AMOUNT'].sum()
    total_crawl_count = result_df['TIME'].count()

    abnormal_criteria = total_crawl_amount / total_crawl_count

    small_df = DataFrame(columns=('TIME', 'AMOUNT'))
    large_df = DataFrame(columns=('TIME', 'AMOUNT'))

    small_index=0
    large_index=0

    for index, row in result_df.iterrows():
        if row['AMOUNT'] < abnormal_criteria:
            small_df.loc[small_index] = [row.TIME, row['AMOUNT']]
            small_index +=1
        else:
            large_df.loc[large_index] = [row.TIME, row['AMOUNT']]
            large_index +=1


    df_list = [small_df, large_df]
    scatter_small = go.Scatter(x = small_df['TIME'],
                               y = small_df['AMOUNT'],
                               mode = 'markers',
                               name = 'below the average',
                               marker = marker1)
    scatter_large = go.Scatter(x = large_df['TIME'],
                               y = large_df['AMOUNT'],
                               mode = 'markers',
                               name = 'above the average',
                               marker = marker2)
    line_graph = go.Scatter( x = result_df['TIME'],
                             y = result_df['AMOUNT'],
                             mode = 'lines+markers',
                             name = 'total lines',
                             marker = marker3
                             )
    
    time_msg = '15분'


    print(time_msg + '그래프가 출력되었습니다.')


    return {
            'data': [line_graph, scatter_small, scatter_large],
            'layout' : go.Layout(
                        title= company_type + " 시간당 크롤량  (" + time_msg + " 기준)",
                        xaxis = dict(title = 'Time'),
                        yaxis = dict(title = 'Crawling Count'),
                        )
            }


def draw_markdown_item_part(n_clicks, startdate_input, enddate_input, company_type, time):
    start_day = date_str_to_datetime(startdate_input)    
    end_day = date_str_to_datetime(enddate_input)
    
    end_tmp = end_day.strftime("%Y-%m-%d")
    end_tmp = str(end_tmp) + " 23:59:59"

    start_date = start_day
    end_date = datetime.datetime.strptime(str(end_tmp) ,'%Y-%m-%d %H:%M:%S')


    epopcon_engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.118:3306/eums-poi", pool_size=20, pool_recycle=3600,
                           connect_args={'connect_timeout': 1000000})
    query = """
    SELECT TIME, SITE, AMOUNT
    FROM CRAWLING_AMOUNT
    WHERE TIME BETWEEN '{}' and '{}' and SITE = '{}'
    """.format(start_date, end_date, company_type)

    result_df = pd.read_sql_query(query, epopcon_engine)    

    if result_df.empty:
        text = """
            ## PERIOD               : %s ~ %s
            ##
            ## 해당 날짜에 데이터가 존재하지 않습니다.
            ## 


        """%(startdate_input, enddate_input)
        return text

    total_crawl_amount = result_df['AMOUNT'].sum()
    total_crawl_count = result_df['AMOUNT'].count()

    text = '''
            # PERIOD               : %s ~ %s
            # TOTAL   CRAWL AMOUNT : %s
            # TOTAL   CRAWL COUNT  : %s
            # AVERAGE CRAWL AMOUNT : %s'''%(startdate_input, enddate_input, total_crawl_amount, total_crawl_count, total_crawl_amount/total_crawl_count)

    return text




@app.callback(
    Output('feature-graphic', 'figure'),
    [Input('submit_button', 'n_clicks')],
    [State('column_type', 'value'),
     State('startdate_input', 'value'),
     State('enddate_input', 'value'),
     State('company_type', 'value'),])

def update_graph(n_clicks, column_type,startdate_input,enddate_input, company_type ):
    time = '15T'
    return draw_graph_item_part(n_clicks,startdate_input,enddate_input, company_type, time)

@app.callback(
    Output('content_text', 'children'),
    [Input('submit_button', 'n_clicks')],
    [State('column_type', 'value'),
     State('startdate_input', 'value'),
     State('enddate_input', 'value'),
     State('company_type', 'value')])

def update_markdown(n_clicks, column_type, startdate_input, enddate_input, company_type):
    time = '15T'
    return draw_markdown_item_part(n_clicks, startdate_input, enddate_input, company_type, time)



if __name__ == '__main__':

    a = pd.read_parquet("colt_item_site_list.PQ")

    st11_list = a[a['SITE_NAME']=='11st'].ID
    Coupang_list = a[a['SITE_NAME']=='Coupang'].ID
    DESCENTE_list = a[a['SITE_NAME']=='DESCENTE'].ID
    DarkVictory_list = a[a['SITE_NAME']=='DarkVictory'].ID
    GMARKET_list = a[a['SITE_NAME']=='GMARKET'].ID
    GSSHOP_list = a[a['SITE_NAME']=='GSSHOP'].ID
    
    #gmarket 같은게 2개
    gmarket2_list = a[a['SITE_NAME']=='Gmarket'].ID
    
    HMALL_list = a[a['SITE_NAME']=='HMALL'].ID
    HnM_list = a[a['SITE_NAME']=='HnM'].ID
    Jd_list = a[a['SITE_NAME']=='Jd'].ID
    MatchesFashion_list = a[a['SITE_NAME']=='MatchesFashion'].ID
    NIKE_list = a[a['SITE_NAME']=='NIKE'].ID
    OLIVEYOUNG_list = a[a['SITE_NAME']=='OLIVEYOUNG'].ID
    SSG_list = a[a['SITE_NAME']=='SSG'].ID
    Ssense_list = a[a['SITE_NAME']=='Ssense'].ID
    Taobao_list = a[a['SITE_NAME']=='Taobao'].ID
    Tmall_list = a[a['SITE_NAME']=='Tmall'].ID
    adidas_list = a[a['SITE_NAME']=='adidas'].ID
    farfetch_list = a[a['SITE_NAME']=='farfetch'].ID
    
    #사이트명이 lotte.com
    lotte_list = a[a['SITE_NAME']=='lotte.com'].ID
    
    mixxmix_list = a[a['SITE_NAME']=='mixxmix'].ID
    musinsa_list = a[a['SITE_NAME']=='musinsa'].ID
    nbkorea_list = a[a['SITE_NAME']=='nbkorea'].ID
    
    #taobao 같은거 2개
    taobao_list = a[a['SITE_NAME']=='taobao'].ID
    #tmall 같은거 2개
    tmall_list = a[a['SITE_NAME']=='tmall'].ID

    
    app.run_server(host='0.0.0.0',port=8050)
