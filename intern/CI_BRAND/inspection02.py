import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import pandas as pd
import numpy as np
import plotly
import pickle
import datetime
#import dash_auth
import dash
from sqlalchemy import create_engine
import pymysql, pandas as pd
pymysql.install_as_MySQLdb()
import MySQLdb
from tqdm import tqdm

app = dash.Dash()
app.scripts.config.serve_locally = True

app.layout = html.Div([
    html.Div([dt.DataTable(rows=[{}], id='dt_words_pair')], id='div_words_pair', className="container", style={'width':'40%', 'height':'100%','display':'inline-block'}),
    html.Div([html.Button(id='bt1', n_clicks=0, children="X" ) ], style={'text-align':'left', 'width':'10%', 'height':'100%', 'display': 'inline-block'}),


    html.Div([dt.DataTable(rows=[{}], id='dt_cate_pair'),], id='div_cate_pair', className="container", style={'width':'40%', 'height':'100%','display':'inline-block'}),

    html.Div([html.Div(id='my-div'),
    dcc.Input(id='cate', value='modify_cate', type='text'),
    dcc.Input(id='cate1', value='modify_cate1', type='text'),
    dcc.Input(id='tag', value='modify_tag', type='text'),
    html.Button(id='bt2', n_clicks=0, children="modify" )],),

    html.Div([dt.DataTable(rows=[{}], id='dt_pair_samples')], id='div_pair_samples', className="container", style={'width':'100%', 'height':'100%','display':'inline-block'}),

    html.Div(id='result_div'),
    html.Div(id='result_div2'),
    html.Div(id='result_div3'),
    html.Div(id='result_div4'),

], id='page', className="container", style={'text-align':'left', 'width':'100%', 'height':'100%','display':'inline-block'})

@app.callback(
    Output('div_words_pair', 'children'),
    [ Input('bt1', 'n_clicks') ],
    [ State('dt_words_pair', 'rows'), State('dt_words_pair', 'selected_row_indices') ]
    )
def loading_pairs(n_clicks, rows, selected_row_indices):
    if n_clicks == 0:
        print('n_clicks == 0')
        return dt.DataTable(
            rows = pc.to_dict('records'),
            columns = ['brand'],
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            resizable=True,
            max_rows_in_viewport=5,
            #min_width=400,
            id='dt_words_pair'
        )
    else:
        return None






@app.callback(
    Output('div_cate_pair', 'children'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
    )
def cate_pairs(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return None

    selected_rows = [rows[index] for index in selected_row_indices]
    #print(selected_rows[0]['pair'][0])
    brand = selected_rows[0]['brand']
    co_id = pc[pc.brand == brand].co_id.values[0]

    company_engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    query = """
    select CO_NAME, CATE,CATE1,TAG
    from TEMP_COMPANY
    where ID in {}
    """.format(co_id)
    #query = 'select CO_NAME,REP_PHONE_NUM,CATE,CATE1,TAG,ADDR,ROAD_ADDR from MEUMS_COMPANY where (STATUS=1 or STATUS=0) and CO_NAME_R regexp "{}.*{}";'.format(w0, w1)
    c = pd.read_sql_query(query, company_engine)
    #c = c.sample(3000)

    print(len(c), ' db rows')
    freq_cate = pd.DataFrame(c.groupby(['CATE', 'CATE1','TAG']).CO_NAME.count()).reset_index().sort_values(by='CO_NAME', ascending=False)
    freq_cate.columns = ['CATE', 'CATE1', 'TAG', 'COUNT']
    result = dt.DataTable(
        rows = freq_cate.to_dict('records'),
        #columns = ['pair', 'pair_str', 'cnt'],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        resizable=True,
        max_rows_in_viewport=5,
        editable=False,
        column_widths=[100,100,300],
        min_width=500,
        id='dt_cate_pair'
    )
    return result






@app.callback(
    Output('cate', 'value'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
)
## modify를 각 카테고리에서 가장 많은 count 로 업데이트
def update_modify_cate(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return 'modify_cate'

    selected_rows = [rows[index] for index in selected_row_indices]
    #print(selected_rows[0]['pair'][0])
    brand = selected_rows[0]['brand']
    co_id = pc[pc.brand == brand].co_id.values[0]

    company_engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    query = """
    select CO_NAME, CATE,CATE1,TAG
    from TEMP_COMPANY
    where ID in {}
    """.format(co_id)
    #query = 'select CO_NAME,REP_PHONE_NUM,CATE,CATE1,TAG,ADDR,ROAD_ADDR from MEUMS_COMPANY where (STATUS=1 or STATUS=0) and CO_NAME_R regexp "{}.*{}";'.format(w0, w1)
    c = pd.read_sql_query(query, company_engine)
    #c = c.sample(3000)

    freq_cate = pd.DataFrame(c.groupby(['CATE', 'CATE1','TAG']).CO_NAME.count()).sort_values(by='CO_NAME', ascending=False).reset_index()
    freq_cate.columns = ['CATE', 'CATE1', 'TAG', 'COUNT']

    return freq_cate['CATE'][0]






## modify1를 각 카테고리에서 가장 많은 count 로 업데이트
@app.callback(
    Output('cate1', 'value'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
)
## modify1를 각 카테고리에서 가장 많은 count 로 업데이트
def update_modify_cate1(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return 'modify_cate1'

    selected_rows = [rows[index] for index in selected_row_indices]
    #print(selected_rows[0]['pair'][0])
    brand = selected_rows[0]['brand']
    co_id = pc[pc.brand == brand].co_id.values[0]

    company_engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    query = """
    select CO_NAME, CATE,CATE1,TAG
    from TEMP_COMPANY
    where ID in {}
    """.format(co_id)
    #query = 'select CO_NAME,REP_PHONE_NUM,CATE,CATE1,TAG,ADDR,ROAD_ADDR from MEUMS_COMPANY where (STATUS=1 or STATUS=0) and CO_NAME_R regexp "{}.*{}";'.format(w0, w1)
    c = pd.read_sql_query(query, company_engine)
    #c = c.sample(3000)

    freq_cate = pd.DataFrame(c.groupby(['CATE', 'CATE1','TAG']).CO_NAME.count()).sort_values(by='CO_NAME', ascending=False).reset_index()
    freq_cate.columns = ['CATE', 'CATE1', 'TAG', 'COUNT']

    return freq_cate['CATE1'][0]






@app.callback(
    Output('tag', 'value'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
)
## modify1를 각 카테고리에서 가장 많은 count 로 업데이트
def update_modify_tag(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return 'modify_cate1'

    selected_rows = [rows[index] for index in selected_row_indices]
    #print(selected_rows[0]['pair'][0])
    brand = selected_rows[0]['brand']
    co_id = pc[pc.brand == brand].co_id.values[0]

    company_engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    query = """
    select CO_NAME, CATE,CATE1,TAG
    from TEMP_COMPANY
    where ID in {}
    """.format(co_id)
    #query = 'select CO_NAME,REP_PHONE_NUM,CATE,CATE1,TAG,ADDR,ROAD_ADDR from MEUMS_COMPANY where (STATUS=1 or STATUS=0) and CO_NAME_R regexp "{}.*{}";'.format(w0, w1)
    c = pd.read_sql_query(query, company_engine)
    #c = c.sample(3000)

    freq_cate = pd.DataFrame(c.groupby(['CATE', 'CATE1','TAG']).CO_NAME.count()).sort_values(by='CO_NAME', ascending=False).reset_index()
    freq_cate.columns = ['CATE', 'CATE1', 'TAG', 'COUNT']

    return freq_cate['TAG'][0]





@app.callback(
    Output('div_pair_samples', 'children'),
    [ Input('dt_cate_pair', 'selected_row_indices')  ],
    [ State('dt_cate_pair', 'rows'), State('dt_words_pair', 'selected_row_indices'), State('dt_words_pair', 'rows') ]
    )
#
def querying_pairs(cate_indeces, cate_rows, word_indeces, word_rows):
    if cate_indeces == None or len(cate_indeces) == 0:
        return None
    if word_indeces == None or len(word_indeces) == 0:
        return None

    sel_word = [word_rows[i] for i in word_indeces][0]
    sel_cate = [cate_rows[i] for i in cate_indeces][0]

    brand = sel_word['brand']
    co_id = pc[pc.brand == brand].co_id.values[0]
    cate = sel_cate['CATE']
    cate1 = sel_cate['CATE1']
    tag = sel_cate['TAG']
    print(brand, cate, cate1, tag)

    query = """
    select ID,CO_NAME,CATE,CATE1,TAG,UPT_DT
    from TEMP_COMPANY
    where ID in {} and CATE = '{}' and CATE1 = '{}' and TAG = '{}'
    """.format(co_id, cate,cate1,tag)

    company_engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )
    c = pd.read_sql_query(query, company_engine)

    return dt.DataTable(
        rows = c.to_dict('records'),
        #columns = ['pair', 'pair_str', 'cnt'],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        resizable=True,
        max_rows_in_viewport=20,
        editable=False,
        column_widths=[100,300,100,80,400,400],
        min_width=1800,
        id='dt_pair_samples'
    )





@app.callback(
    Output('result_div2', component_property='children'),
    [Input('bt2', 'n_clicks'),],
    [State('dt_cate_pair', 'selected_row_indices'),
     State('dt_cate_pair', 'rows'),
     State('dt_words_pair', 'selected_row_indices'),
     State('dt_words_pair', 'rows'),
     State('dt_pair_samples', 'selected_row_indices'),
     State('dt_pair_samples', 'rows'),
     State('cate', 'value'),
     State('cate1','value'),
     State('tag','value')]
    )
## DB값을 실제로 업데이트
def modify_print(n_clicks, cate_indeces, cate_rows, word_indeces, word_rows, sample_indeces, sample_rows, modify_cate, modify_cate1, modify_tag):
    if cate_indeces == None or len(cate_indeces) == 0:
        return None
    if word_indeces == None or len(word_indeces) == 0:
        return None
    if modify_cate == None or modify_cate1 == None or n_clicks == 0:
        return None


    sel_word = [word_rows[i] for i in word_indeces][0]
    sel_cate = [cate_rows[i] for i in cate_indeces][0]

    brand = sel_word['brand']
    co_id = pc[pc.brand == brand].co_id.values[0]
    cate = sel_cate['CATE']
    cate1 = sel_cate['CATE1']
    tag = sel_cate['TAG']

    print(brand, cate, cate1,tag)

    engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    #UPDATE 할 CATE_CODE 가져옴 #cate_code = 바꿀 카테의 코드
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '' """.format(modify_cate)#, modify_cate1)
    modi_cate_code = pd.read_sql_query(code_query, engine)
    after_cate_code = modi_cate_code['CODE'][0]

    #UPDATE 할 CATE_CODE1 가져옴  #cate1_code = 바꿀 카테1의 코드
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '{}' """.format(modify_cate1, after_cate_code)
    if modify_cate1 =="":
        after_cate1_code = ""
    else:
        modi_cate1_code = pd.read_sql_query(code_query, engine)
        after_cate1_code = modi_cate1_code['CODE'][0]

    #UPDATE 전 CATE_CODE 가져옴
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '' """.format(cate)#, modify_cate1)
    select_cate_code = pd.read_sql_query(code_query, engine)
    before_cate_code = select_cate_code['CODE'][0]

    #UPDATE 전 CATE_CODE1 가져옴  #cate1_code = 바꿀 카테1의 코드
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '{}' """.format(cate1, before_cate_code)
    if cate1== "":
        before_cate1_code = ""
    else:
        select_cate1_code = pd.read_sql_query(code_query, engine)
        before_cate1_code = select_cate1_code['CODE'][0]


    company_id = []
    for i in sample_indeces:
        company_id.append(str(sample_rows[i]['ID']))
    company_id = tuple(company_id)

    try:
        query = """
        UPDATE TEMP_COMPANY
        SET CATE_CODE = "{}", CATE = "{}" , CATE1_CODE = "{}", CATE1 ="{}", TAG = '{}',UPT_DT = "{}", MODIFIER = "{}"
        where ID in {}
        """.format(after_cate_code, modify_cate, after_cate1_code, modify_cate1,modify_tag, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'KOOKMIN', company_id)


        with engine.connect() as con:
            con.execute(query)
    except:
        company_id = str(sample_rows[i]['ID'])
        query = """
        UPDATE TEMP_COMPANY
        SET CATE_CODE = "{}", CATE = "{}" , CATE1_CODE = "{}", CATE1 ="{}", TAG = '{}',UPT_DT = "{}", MODIFIER = "{}"
        where ID = '{}'
        """.format(after_cate_code, modify_cate, after_cate1_code, modify_cate1,modify_tag, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'KOOKMIN', company_id)


        with engine.connect() as con:
            con.execute(query)


    for i in tqdm(sample_indeces):
        query2 = """
        INSERT INTO TEMP_COMPANY_UPDATE_HISTORY
        SET COMPANY_ID = '{}', CO_NAME = '{}', PAIR1 = '{}', PAIR2 = '{}', ORG_CATE_CODE = '{}',ORG_CATE1_CODE = '{}', ORG_CATE = '{}', ORG_CATE1 = '{}', CATE_CODE = '{}', CATE1_CODE = '{}', CATE = '{}', CATE1 = '{}', MODIFIER = '{}', UPT_DT = '{}'
        """.format(sample_rows[i]['ID'],
        sample_rows[i]['CO_NAME'],
        brand,
        brand,
        before_cate_code,
        before_cate1_code,
        cate,
        cate1,
        after_cate_code,
        after_cate1_code,
        modify_cate, modify_cate1,'KOOKMIN',
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))



        with engine.connect() as con:
            con.execute(query2)




    return 'DB 수정 완료'





if __name__ == '__main__':
    pc = pd.read_pickle('final_brand_result.pkl')
    app.run_server(debug = True)
