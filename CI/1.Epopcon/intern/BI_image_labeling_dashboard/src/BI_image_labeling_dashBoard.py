# Perform imports here:
import numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from sqlalchemy import create_engine
from dash.dependencies import Input, Output, State
import math
from math import radians, cos, sin, asin, sqrt
import dash_table_experiments as dt
from fastparquet import ParquetFile

wspidermr_engine = create_engine("mysql+pymysql://wspidermr:wspidermr00!q@133.186.134.155:3306/lf-bigdata-real-5?charset=utf8mb4",
                   encoding = 'utf8',
                   pool_size=20,
                   pool_recycle=3600,
                   connect_args={'connect_timeout':1000000} )

#카테고리 정보를 가져오기
category_query = """
select *
from MLF_CATEGORY
"""
#사이트 정보를 가져오기
site_query = """
select *
from MLF_SITE
"""
category = pd.read_sql_query(category_query, wspidermr_engine)
site = pd.read_sql_query(site_query, wspidermr_engine)

#최종 결과물(image들)을 가져오기 위한 전역변수 image_list
image_list = 0

#dash site
app = dash.Dash()
app.scripts.config.serve_locally = True
app.config.supress_callback_exceptions = True

#depth가 1인 category name을 담기위한 리스트
big_OPTION = []
#depth가 2인 category name을 담기위한 리스트
mid_OPTION = []
#depth가 3인 category name을 담기위한 리스트
small_OPTION = []

big_cate_list = category[category.DEPTH == 1][['CATE_NO', 'CATE_NAME']].reset_index()
for idx in range(0,len(big_cate_list)):
    big_OPTION.append({'label':big_cate_list['CATE_NAME'][idx], 'value': big_cate_list['CATE_NO'][idx]})


app.layout = html.Div([
        #카테고리 별 이미지를 위한 Dropdown
        html.Div([dcc.Dropdown(id = 'big_name',options = big_OPTION,value = 'ID'),
                dcc.Dropdown(id = 'mid_name',options = mid_OPTION,value = 'ID'),
                dcc.Dropdown(id = 'small_name',options = small_OPTION,value = 'ID')], style = {'width': 400,'height':70,"text-align":"center"}),
        #image_list를 저장하기 위해 만든 output장소 (no display)
        html.Br(id = 'no_area'),
        #버튼
        html.Div([html.Button(id = 'submit-button', n_clicks= 0, children = 'Submit', style = {'fontSize':20, 'height':100})],),
        #html.Div([dt.DataTable(rows=[{}], id='dt_data_pair')], id='div_data_pair', className="container", style={'width': "100%",'display':'inline-block'}),
        # html.Div([html.Img(id = 'image',),], id = 'div_image', style={'width': "100%",'display':'inline-block'}),
        dcc.Location(id='url', refresh=False),
        #pagination
        html.Div(id='page-content', className='pagination')
])
@app.callback(
    Output('no_area', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('small_name', 'value')]
)
def returnID_list(n_click, cate_no):
    global image_list
    #db 연결
    wspidermr_engine = create_engine("mysql+pymysql://wspidermr:wspidermr00!q@133.186.134.155:3306/lf-bigdata-real-5?charset=utf8mb4",
                       encoding = 'utf8',
                       pool_size=20,
                       pool_recycle=3600,
                       connect_args={'connect_timeout':1000000} )
    wspider_engine = create_engine("mysql+pymysql://wspider:wspider00!q@133.186.143.65:3306/wspider?charset=utf8mb4",
                       encoding = 'utf8',
                       pool_size=20,
                       pool_recycle=3600,
                       connect_args={'connect_timeout':1000000} )


    #버튼으로 넘겨받은 카테고리에 해당하는 굿즈 넘버 반환
    query = """select * from MLF_GOODS_CATE where CATE_NO = {} limit 10000""".format(cate_no)
    good_no = pd.read_sql_query(query, wspidermr_engine)
    goods_no = good_no.GOODS_NO.unique()

    #넘겨 받은 굿즈넘버를 통해 해당 사이트 이름과 아이템 넘버를 반환
    query = """select * from MLF_GOODS where GOODS_NO in {} limit 10000 """.format(tuple(goods_no))
    goods = pd.read_sql_query(query, wspidermr_engine)
    goods = pd.merge(goods,site, on = 'SITE_NO')
    goods = goods[['SITE_NAME', 'ITEM_NUM']]
    sitenames = goods.SITE_NAME.unique()

    #사이트 이름별로 해당 카테고리 아이템을 각각 천개씩 저장(hmall, gs, lotte)
    ID_list = []
    for name in sitenames:
        ID = tuple(goods[goods.SITE_NAME == name].ITEM_NUM.unique())
        query = """
        select ID
        from MWS_COLT_ITEM
        where ITEM_NUM in {} and SITE_NAME = '{}'
        limit 1000
        """.format(ID, name)
        temp = pd.read_sql_query(query, wspider_engine)
        print(len(temp),name)
        if len(temp) == 0:
            continue
        else:
            ID_list.append(temp)

    if len(ID_list) == 1:
        id_list = ID_list
    else:
        id_list = pd.concat(ID_list)

    print(len(id_list))


    #각 사이트별 1000개씩 받은 아이템 id를 통해 image 반환
    query = """
    select GOODS_IMAGE
    from MWS_COLT_IMAGE
    where ITEM_ID in {}
    limit 2000
    """.format(tuple(id_list['ID'].unique()))
    image = pd.read_sql_query(query, wspider_engine)
    image_list = image

#관리하기 편하게 인덱스 페이지 생성 하였으나 별로 필요 없는거 같아서 주석처리
# index_page = html.Div([
#      dcc.Link('Go to Page 1', href='/page-1'),
#      html.Br(),
#      dcc.Link('Go to Page 2', href='/page-2'),
#      html.Br(),
#      dcc.Link('Go to Page 3', href='/page-3'),
#      html.Br(),
#      dcc.Link('Go to Page 4', href='/page-4'),
#      html.Br(),
#      dcc.Link('Go to Page 5', href='/page-5'),
#      html.Br(),
#      dcc.Link('Go to Page 6', href='/page-6'),
#      html.Br(),
#      dcc.Link('Go to Page 7', href='/page-7'),
#      html.Br(),
#      dcc.Link('Go to Page 8', href='/page-8'),
#      html.Br(),
#      dcc.Link('Go to Page 9', href='/page-9'),
#      html.Br(),
#      dcc.Link('Go to Page 10', href='/page-10'),
# ])

#page1 에 보여지는 image
page1 = html.Div([
     html.Br(),
     dcc.Link('Go to Page 2', href='/page-2'),
     html.Div([html.Img(id = 'image1',),], id = 'div_image1', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image1', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    print(len(image_list))
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[0:int(len(image_list['GOODS_IMAGE'])/10)]]

#page2 에 보여지는 image
page2 = html.Div([
     dcc.Link('Go to Page 1', href='/page-1'),
     html.Br(),
     dcc.Link('Go to Page 3', href='/page-3'),
     html.Div([html.Img(id = 'image2',),], id = 'div_image2', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image2', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)+1:int(len(image_list['GOODS_IMAGE'])/10)*2]]

#page3 에 보여지는 image
page3 = html.Div([
     dcc.Link('Go to Page 2', href='/page-2'),
     html.Br(),
     dcc.Link('Go to Page 4', href='/page-4'),
     html.Div([html.Img(id = 'image3',),], id = 'div_image3', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image3', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*2:int(len(image_list['GOODS_IMAGE'])/10)*3]]

#page4 에 보여지는 image
page4 = html.Div([
     dcc.Link('Go to Page 3', href='/page-3'),
     html.Br(),
     dcc.Link('Go to Page 5', href='/page-5'),
     html.Div([html.Img(id = 'image4',),], id = 'div_image4', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image4', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*3:int(len(image_list['GOODS_IMAGE'])/10)*4]]

#page5 에 보여지는 image
page5 = html.Div([
     dcc.Link('Go to Page 4', href='/page-4'),
     html.Br(),
     dcc.Link('Go to Page 6', href='/page-6'),
     html.Div([html.Img(id = 'image5',),], id = 'div_image5', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image5', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*4:int(len(image_list['GOODS_IMAGE'])/10)*5]]

#page6 에 보여지는 image
page6 = html.Div([
     dcc.Link('Go to Page 5', href='/page-5'),
     html.Br(),
     dcc.Link('Go to Page 7', href='/page-7'),
     html.Div([html.Img(id = 'image6',),], id = 'div_image6', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image6', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*5:int(len(image_list['GOODS_IMAGE'])/10)*6]]

#page7 에 보여지는 image
page7 = html.Div([
     dcc.Link('Go to Page 6', href='/page-6'),
     html.Br(),
     dcc.Link('Go to Page 8', href='/page-8'),
     html.Div([html.Img(id = 'image7',),], id = 'div_image7', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image7', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*6:int(len(image_list['GOODS_IMAGE'])/10)*7]]

#page8 에 보여지는 image
page8 = html.Div([
     dcc.Link('Go to Page 7', href='/page-7'),
     html.Br(),
     dcc.Link('Go to Page 9', href='/page-9'),
     html.Div([html.Img(id = 'image8',),], id = 'div_image8', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image8', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*7:int(len(image_list['GOODS_IMAGE'])/10)*8]]

#page9 에 보여지는 image
page9 = html.Div([
     dcc.Link('Go to Page 8', href='/page-8'),
     html.Br(),
     dcc.Link('Go to Page 10', href='/page-10'),
     html.Div([html.Img(id = 'image9',),], id = 'div_image9', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image9', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*8:int(len(image_list['GOODS_IMAGE'])/10)*9]]

#page10 에 보여지는 image
page10 = html.Div([
     dcc.Link('Go to Page 9', href='/page-9'),
     html.Br(),
     dcc.Link('Go to Page 1', href='/page-1'),
     html.Div([html.Img(id = 'image10',),], id = 'div_image10', style={'width': "100%",'display':'inline-block'}),
])
@app.callback(
Output('div_image10', 'children'),
[Input('url', 'pathname')],)
def display_image1(pathname):
    global image_list
    if pathname == None:
        return None
    return [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])[int(len(image_list['GOODS_IMAGE'])/10)*9:]]

#pagination 시 page 이동을 위한 callback
@app.callback(
Output('page-content', 'children'),
[Input('url', 'pathname')],)
def display_page(pathname):
    if pathname == '/page-1':
         return page1
    elif pathname == '/page-2':
        return page2
    elif pathname == '/page-3':
        return page3
    elif pathname == '/page-4':
        return page4
    elif pathname == '/page-5':
        return page5
    elif pathname == '/page-6':
        return page6
    elif pathname == '/page-7':
        return page7
    elif pathname == '/page-8':
        return page8
    elif pathname == '/page-9':
        return page9
    elif pathname == '/page-10':
        return page10
    else:
        return page1


#depth가 1인 category name을 통해 mid_name 을 불러오기 위한 콜백
@app.callback(
    Output('mid_name', 'options'),
    [Input('big_name', 'value')],
)
def get_mid_name(cate_no):
    if cate_no == None:
        return None

    mid_OPTION = []
    global category
    mid_OPTION = []
    midcate = category[category.UPPER_CATE_NO == cate_no]
    mid_cate_list = midcate[midcate.DEPTH == 2][['CATE_NO', 'CATE_NAME']].reset_index()
    for idx in range(0,len(mid_cate_list)):
        mid_OPTION.append({'label':mid_cate_list['CATE_NAME'][idx], 'value': mid_cate_list['CATE_NO'][idx]})

    return mid_OPTION

#depth가 2인 category name을 통해 small_name 을 불러오기 위한 콜백
@app.callback(
    Output('small_name', 'options'),
    [Input('mid_name', 'value')],
)
def get_small_name(cate_no):
    if cate_no == None:
        return None

    small_OPTION = []
    global category
    smallcate = category[category.UPPER_CATE_NO == cate_no]
    small_cate_list = smallcate[smallcate.DEPTH == 3][['CATE_NO', 'CATE_NAME']].reset_index()
    for idx in range(0,len(small_cate_list)):
        small_OPTION.append({'label':small_cate_list['CATE_NAME'][idx], 'value': small_cate_list['CATE_NO'][idx]})

    return small_OPTION


external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Raleway',
    '//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]

for css in external_css:
    app.css.append_css({'external_url': css})



if __name__ == '__main__':
    app.run_server(host = '0.0.0.0', port=8050, debug = True)
