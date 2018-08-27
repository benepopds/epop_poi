import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import plotly.plotly as py
import squarify
import json
import pandas as pd
import numpy as np
import plotly
import pickle
import datetime
#import dash_auth
import dash_auth
from sqlalchemy import create_engine
import pymysql, pandas as pd
pymysql.install_as_MySQLdb()
import MySQLdb



df = pd.read_parquet('TEMP_COMPANY_REFINE.PQ')
modify_dict = {}


VALID_USERNAME_PASSWORD_PAIRS = [
    ['admin1', 'epop0313'],
    ['admin2', 'epop0313'],
    ['admin3', 'epop0313'],
]

app = dash.Dash('auth')
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

user_name = auth._username

print(type(auth))
print(auth._username)
print(type(auth._username))


## PQ 파일 sync 맞추는 작업은 나중에 서버 올라가고 나서 코어 여러개 쓰는 방안 고민해보기 (패럴)


#app = dash.Dash('auth')
app.layout = html.Div([
    html.Div([dt.DataTable(rows=[{}], id='dt_words_pair')], id='div_words_pair', className="container", style={'width':'40%', 'height':'100%','display':'inline-block'}),
    html.Div([html.Button(id='bt1', n_clicks=0, children="X" ) ], style={'text-align':'left', 'width':'10%', 'height':'100%', 'display': 'inline-block'}),


    html.Div([dt.DataTable(rows=[{}], id='dt_cate_pair'),], id='div_cate_pair', className="container", style={'width':'40%', 'height':'100%','display':'inline-block'}),

    html.Div([html.Div(id='my-div'),dcc.Input(id='cate', value='modify_cate', type='text'),dcc.Input(id='cate1', value='modify_cate1', type='text'),
    html.Button(id='bt2', n_clicks=0, children="modify" )],),

    html.Button(id='bt3', n_clicks=0, children = '상점찾기제외'),
    html.Button(id='bt4', n_clicks=0, children = 'Sync DB - PQ'),

    html.Div([dt.DataTable(rows=[{}], id='dt_pair_samples')], id='div_pair_samples', className="container", style={'width':'100%', 'height':'100%','display':'inline-block'}),

    html.Div(id='result_div'),
    html.Div(id='result_div2'),
    html.Div(id='result_div3'),
    html.Div(id='result_div4'),

], id='page', className="container", style={'text-align':'left', 'width':'100%', 'height':'100%','display':'inline-block'})


@app.callback(
    Output('result_div4', component_property='children'),
    [ Input('bt4', 'n_clicks')],
)

def click_save_button(n_clicks):
    if n_clicks==0:
        return None
    engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )
    query = """select ID, CO_NAME, CO_NAME_R, REP_PHONE_NUM, ADDR, ROAD_ADDR, CATE_CODE, CATE, CATE1_CODE, CATE1, TAG, STATUS, MODIFIER, UPT_DT from TEMP_COMPANY """
    df = pd.read_sql_query(query, engine)
    df.to_parquet('TEMP_COMPANY_REFINE.PQ')
    return 'PARQUET UPDATE SUCCESS'





## modify를 각 카테고리에서 가장 많은 count 로 업데이트
@app.callback(
    Output('cate', 'value'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
)

## modify를 각 카테고리에서 가장 많은 count 로 업데이트
def update_modify_cate(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return 'modify_cate'

    result=""

    selected_rows = [rows[index] for index in selected_row_indices]
    w0, w1 = selected_rows[0]['pair'][0], selected_rows[0]['pair'][1]


    df2 = df[(df['CO_NAME_R'].str.contains('{}.*{}'.format(w0, w1) , regex = True, na = False )) & ((df['STATUS'] == '0' ) | (df['STATUS'] == '1'))]

    freq_cate = pd.DataFrame(df2.groupby(['CATE', 'CATE1']).CO_NAME.count()).reset_index().sort_values(by='CO_NAME', ascending=False)
    result = freq_cate['CATE'].values[0]
    return result

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

    result=""

    selected_rows = [rows[index] for index in selected_row_indices]
    w0, w1 = selected_rows[0]['pair'][0], selected_rows[0]['pair'][1]


    df2 = df[(df['CO_NAME_R'].str.contains('{}.*{}'.format(w0, w1) , regex = True, na = False )) & ((df['STATUS'] == '0' ) | (df['STATUS'] == '1'))]
    freq_cate = pd.DataFrame(df2.groupby(['CATE', 'CATE1']).CO_NAME.count()).reset_index().sort_values(by='CO_NAME', ascending=False)
    result = freq_cate['CATE1'].values[0]
    return result




@app.callback(
    Output('result_div',component_property='children'),
    [Input('bt3', 'n_clicks'),
     Input('dt_pair_samples', 'selected_row_indices'),
     Input('dt_pair_samples', 'rows'),],
    [State('dt_cate_pair', 'selected_row_indices'),
    State('dt_cate_pair', 'rows'),
    State('dt_words_pair', 'selected_row_indices'),
    State('dt_words_pair', 'rows'),
    State('cate', 'value'),
    State('cate1','value')]
)

def exclude_store(n_clicks, sample_indeces, sample_rows, cate_indeces, cate_rows, word_indeces, word_rows, modify_cate, modify_cate1):
    if cate_indeces == None or len(cate_indeces) == 0:
        return ""
    if word_indeces == None or len(word_indeces) == 0:
        return ""
    if modify_cate == None or modify_cate1 == None or n_clicks == 0:
        return ""


    sel_word = [word_rows[i] for i in word_indeces][0]
    sel_cate = [cate_rows[i] for i in cate_indeces][0]

    w0 = sel_word['pair'][0] #내가찍은 pair 1
    w1 = sel_word['pair'][1] #내가찍은 pair 2
    cate_select = sel_cate['CATE']   #내가찍은 cate
    cate1_select = sel_cate['CATE1'] #내가찍은 cate1

    print(w0, w1, cate_select, cate1_select)

    print('## test!!! ')
    print(sample_indeces)
    print(type(sample_indeces))

    engine = create_engine("mysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' , pool_size=50,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

    #기존 CATE_CODE 가져옴
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '' """.format(cate_select)#, modify_cate1)
    select_cate_code = pd.read_sql_query(code_query, engine)
    before_cate_code = select_cate_code['CODE'][0]

    #기존 CATE_CODE1 가져옴
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '{}' """.format(cate1_select, before_cate_code)
    if cate1_select == "":
        before_cate1_code = ""
    else:
        select_cate1_code = pd.read_sql_query(code_query, engine)
        before_cate1_code = select_cate1_code['CODE'][0]

    for i in range(0, len(sample_indeces)):
        c = df[(df['CO_NAME'] == sample_rows[i]['CO_NAME']) & (df['REP_PHONE_NUM'] == sample_rows[i]['REP_PHONE_NUM']) & (df['CATE'] == cate_select) & (df['CATE1'] == cate1_select) & ( (df['STATUS'] == '0') | (df['STATUS'] == '1' ) ) ]
        company_id = c['ID'].values[0]
        origin_status = c['STATUS'].values[0]

        query = """
        UPDATE TEMP_COMPANY
        SET STATUS = "{}", UPT_DT = "{}", MODIFIER = "{}"
        where (STATUS=1 or STATUS=0) and CO_NAME = "{}" and REP_PHONE_NUM = "{}" and CATE="{}" and CATE1="{}"
        """.format(-9, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),auth._username, sample_rows[i]['CO_NAME'], sample_rows[i]['REP_PHONE_NUM'],cate_select, cate1_select)

        print(query)
        with engine.connect() as con:
            con.execute(query)

        query2 = """
        INSERT INTO TEMP_COMPANY_EXCLUDE_HISTORY
        SET COMPANY_ID = '{}', CO_NAME = '{}', CATE_CODE = '{}',CATE1_CODE = '{}', CATE = '{}', CATE1 = '{}', STATUS = '{}',  MODIFIER = '{}', UPT_DT = '{}'
        """.format(company_id, sample_rows[i]['CO_NAME'], before_cate_code, before_cate1_code, cate_select,cate1_select,origin_status ,auth._username ,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(query2)
        with engine.connect() as con:
            con.execute(query2)

    return '선택하신 정보의 STATUS 를 -9로 변경하였습니다.'


## DB값을 실제로 업데이트
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
     State('cate1','value')]
    )

## DB값을 실제로 업데이트
def modify_print(n_clicks, cate_indeces, cate_rows, word_indeces, word_rows, sample_indeces, sample_rows, modify_cate, modify_cate1):
    if cate_indeces == None or len(cate_indeces) == 0:
        return None
    if word_indeces == None or len(word_indeces) == 0:
        return None
    if modify_cate == None or modify_cate1 == None or n_clicks == 0:
        return None

    print(cate_indeces, len(cate_rows), word_indeces, len(word_rows))

    sel_word = [word_rows[i] for i in word_indeces][0]
    sel_cate = [cate_rows[i] for i in cate_indeces][0]

    w0 = sel_word['pair'][0] #내가찍은 pair 1
    w1 = sel_word['pair'][1] #내가찍은 pair 2
    cate_select = sel_cate['CATE']   #내가찍은 cate
    cate1_select = sel_cate['CATE1'] #내가찍은 cate1

    print(w0, w1, cate_select, cate1_select)

    print('## test!!! ')
    print(sample_indeces)
    print(type(sample_indeces))

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
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '' """.format(cate_select)#, modify_cate1)
    select_cate_code = pd.read_sql_query(code_query, engine)
    before_cate_code = select_cate_code['CODE'][0]

    #UPDATE 전 CATE_CODE1 가져옴  #cate1_code = 바꿀 카테1의 코드
    code_query = """select CODE from MEUMS_CODE where CODE_NAME = '{}' and GROUP_CODE = 'COMPCATE' and UPPER_CODE = '{}' """.format(cate1_select, before_cate_code)
    if cate1_select == "":
        before_cate1_code = ""
    else:
        select_cate1_code = pd.read_sql_query(code_query, engine)
        before_cate1_code = select_cate1_code['CODE'][0]

    for i in range(0, len(sample_indeces)):
        c = df[(df['CO_NAME'] == sample_rows[i]['CO_NAME']) & (df['REP_PHONE_NUM'] == sample_rows[i]['REP_PHONE_NUM']) & (df['CATE'] == cate_select) & (df['CATE1'] == cate1_select)  & (  (df['STATUS']=='0') | (df['STATUS'] == '1') )   ]
        print('###')
        print(c)

        company_id = c['ID'].values[0]


        query = """
        UPDATE TEMP_COMPANY
        SET CATE_CODE = "{}", CATE = "{}" , CATE1_CODE = "{}", CATE1 ="{}", UPT_DT = "{}", MODIFIER = "{}"
        where (STATUS=1 or STATUS=0) and CO_NAME = "{}" and REP_PHONE_NUM = "{}" and CATE="{}" and CATE1="{}"
        """.format(after_cate_code, modify_cate, after_cate1_code, modify_cate1, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),auth._username, sample_rows[i]['CO_NAME'], sample_rows[i]['REP_PHONE_NUM'],cate_select, cate1_select)

        print(query)
        with engine.connect() as con:
            con.execute(query)



        query2 = """
        INSERT INTO TEMP_COMPANY_UPDATE_HISTORY
        SET COMPANY_ID = '{}', CO_NAME = '{}', PAIR1 = '{}', PAIR2 = '{}', ORG_CATE_CODE = '{}',ORG_CATE1_CODE = '{}', ORG_CATE = '{}', ORG_CATE1 = '{}', CATE_CODE = '{}', CATE1_CODE = '{}', CATE = '{}', CATE1 = '{}', MODIFIER = '{}', UPT_DT = '{}'
        """.format(company_id, sample_rows[i]['CO_NAME'],  w0,w1,before_cate_code, before_cate1_code, cate_select,cate1_select,after_cate_code, after_cate1_code,modify_cate, modify_cate1,auth._username ,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        print(query2)
        with engine.connect() as con:
            con.execute(query2)




    return 'DB 수정 완료'




#print div_cate_pair
@app.callback(
    Output('div_cate_pair', 'children'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
    )

def cate_pairs(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return None

    selected_rows = [rows[index] for index in selected_row_indices]

    w0, w1 = selected_rows[0]['pair'][0], selected_rows[0]['pair'][1]

    df2 = df[(df['CO_NAME_R'].str.contains('{}.*{}'.format(w0, w1) , regex = True, na = False )) & ((df['STATUS'] == '0' ) | (df['STATUS'] == '1'))]
    print(df2)

    freq_cate = pd.DataFrame(df2.groupby(['CATE', 'CATE1']).CO_NAME.count()).reset_index().sort_values(by='CO_NAME', ascending=False)
    freq_cate.columns = ['CATE', 'CATE1', 'COUNT']


    return dt.DataTable(
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

#read pkl & show pair
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
            columns = ['pair_str', 'cnt'],
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

#select pair print
@app.callback(
    Output('my-div',component_property='children'),
    [ Input('dt_words_pair', 'selected_row_indices')  ],
    [ State('dt_words_pair', 'rows') ]
    )
def print_div(selected_row_indices, rows):
    if selected_row_indices == None or len(selected_row_indices) == 0:
        return None

    selected_rows = [rows[index] for index in selected_row_indices]

    w0, w1 = selected_rows[0]['pair'][0], selected_rows[0]['pair'][1]
    print (w0, w1)

    return w0, w1

#print select table
@app.callback(
    Output('div_pair_samples', 'children'),
    [ Input('dt_cate_pair', 'selected_row_indices')  ],
    [ State('dt_cate_pair', 'rows'), State('dt_words_pair', 'selected_row_indices'), State('dt_words_pair', 'rows') ]
    )
def querying_pairs(cate_indeces, cate_rows, word_indeces, word_rows):
    if cate_indeces == None or len(cate_indeces) == 0:
        return None
    if word_indeces == None or len(word_indeces) == 0:
        return None

    print(cate_indeces, len(cate_rows), word_indeces, len(word_rows))

    sel_word = [word_rows[i] for i in word_indeces][0]
    sel_cate = [cate_rows[i] for i in cate_indeces][0]

    w0= sel_word['pair'][0]
    w1= sel_word['pair'][1]
    cate=sel_cate['CATE']
    cate1=sel_cate['CATE1']

    print(w0, w1, cate, cate1)

    df2 = df[(df['CO_NAME_R'].str.contains('{}.*{}'.format(w0, w1) , regex = True, na = False )) & ((df['STATUS'] == '0' ) | (df['STATUS'] == '1')) & (df['CATE'] == cate) & (df['CATE1'] == cate1)]
    df2 = df2[['CO_NAME', 'REP_PHONE_NUM', 'CATE', 'CATE1', 'TAG', 'ADDR', 'ROAD_ADDR']]

    return dt.DataTable(
        rows = df2.to_dict('records'),
        #columns = ['pair', 'pair_str', 'cnt'],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        resizable=True,
        max_rows_in_viewport=20,
        editable=False,
        column_widths=[300,100,80,100,400,350,350],
        min_width=1800,
        id='dt_pair_samples'
    )


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':

    try:
        words_pair_count_dontcare = pickle.load(open('words_pair_count_dontcare.list.pkl', 'rb'))
        print('loading dontcare list')
    except:
        words_pair_count_dontcare = []

    pc_list = pickle.load(open('words_pair_count_sorted.list.pkl', 'rb'))
    pc_list = pc_list[:2000]
    pc_list = [pce for pce in pc_list if pce not in words_pair_count_dontcare]
    pc = pd.DataFrame(pc_list, columns=['pair','cnt'])
    pc['pair_str'] = pc.pair.astype('str')

    print('## user name ##')
    print(user_name)

    app.run_server(debug=False, host='0.0.0.0', port=8050)
