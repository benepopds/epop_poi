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
category_query = """
select *
from MLF_CATEGORY
"""
site_query = """
select *
from MLF_SITE
"""
category = pd.read_sql_query(category_query, wspidermr_engine)
site = pd.read_sql_query(site_query, wspidermr_engine)

image_list = 0
app = dash.Dash()
app.scripts.config.serve_locally = True
app.config.supress_callback_exceptions = True

big_OPTION = []
mid_OPTION = []
small_OPTION = []
big_cate_list = category[category.DEPTH == 1][['CATE_NO', 'CATE_NAME']].reset_index()
for idx in range(0,len(big_cate_list)):
    big_OPTION.append({'label':big_cate_list['CATE_NAME'][idx], 'value': big_cate_list['CATE_NO'][idx]})


app.layout = html.Div([
        html.Div([dcc.Dropdown(id = 'big_name',options = big_OPTION,value = 'ID'),
                dcc.Dropdown(id = 'mid_name',options = mid_OPTION,value = 'ID'),
                dcc.Dropdown(id = 'small_name',options = small_OPTION,value = 'ID')], style = {'width': 400,'height':70,"text-align":"center"}),
        html.Br(id = 'no_area'),
        html.Div([html.Button(id = 'submit-button', n_clicks= 0, children = 'Submit', style = {'fontSize':20, 'height':100})],),
        #html.Div([dt.DataTable(rows=[{}], id='dt_data_pair')], id='div_data_pair', className="container", style={'width': "100%",'display':'inline-block'}),
        # html.Div([html.Img(id = 'image',),], id = 'div_image', style={'width': "100%",'display':'inline-block'}),
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content', className='pagination')
])
@app.callback(
    Output('no_area', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('small_name', 'value')]
)
def returnID_list(n_click, cate_no):
    global image_list
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



    query = """select * from MLF_GOODS_CATE where CATE_NO = {} limit 10000""".format(cate_no)
    good_no = pd.read_sql_query(query, wspidermr_engine)
    goods_no = good_no.GOODS_NO.unique()


    query = """select * from MLF_GOODS where GOODS_NO in {} limit 10000 """.format(tuple(goods_no))
    goods = pd.read_sql_query(query, wspidermr_engine)
    goods = pd.merge(goods,site, on = 'SITE_NO')
    goods = goods[['SITE_NAME', 'ITEM_NUM']]
    sitenames = goods.SITE_NAME.unique()

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

    query = """
    select GOODS_IMAGE
    from MWS_COLT_IMAGE
    where ITEM_ID in {}
    limit 2000
    """.format(tuple(id_list['ID'].unique()))
    image = pd.read_sql_query(query, wspider_engine)
    image_list = image
    # [html.Img(id = 'image',src = image,height = 150, width = 150)for image in list(image_list['GOODS_IMAGE'])]
    # return dt.DataTable(
    # rows = image_list.to_dict('records'),
    # #columns = ['pair', 'pair_str', 'cnt'],
    # row_selectable=True,
    # filterable=True,
    # sortable=True,
    # selected_row_indices=[],
    # resizable=True,
    # max_rows_in_viewport=5,
    # editable=False,
    # min_width=2000,
    # id='dt_data_pair'
    # )
index_page = html.Div([
     dcc.Link('Go to Page 1', href='/page-1'),
     html.Br(),
     dcc.Link('Go to Page 2', href='/page-2'),
     html.Br(),
     dcc.Link('Go to Page 3', href='/page-3'),
     html.Br(),
     dcc.Link('Go to Page 4', href='/page-4'),
     html.Br(),
     dcc.Link('Go to Page 5', href='/page-5'),
     html.Br(),
     dcc.Link('Go to Page 6', href='/page-6'),
     html.Br(),
     dcc.Link('Go to Page 7', href='/page-7'),
     html.Br(),
     dcc.Link('Go to Page 8', href='/page-8'),
     html.Br(),
     dcc.Link('Go to Page 9', href='/page-9'),
     html.Br(),
     dcc.Link('Go to Page 10', href='/page-10'),
])

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


external_js = [
    # jQuery, DataTables, script to initialize DataTables
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    '//cdn.datatables.net/1.10.15/js/jquery.dataTables.min.js',
    # small hack for DataTables
    'https://codepen.io/jackdbd/pen/bROVgV.js',
]

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Raleway',
    '//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    '//cdn.datatables.net/1.10.15/css/jquery.dataTables.min.css',
]

for js in external_js:
    app.scripts.append_script({'external_url': js})

for css in external_css:
    app.css.append_css({'external_url': css})



if __name__ == '__main__':
    app.run_server(host = '0.0.0.0', port=8050, debug = True)
