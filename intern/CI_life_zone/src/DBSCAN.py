
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from sqlalchemy import create_engine
from dash.dependencies import Input, Output, State
from sklearn.cluster import DBSCAN

engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.50:3306/eums?charset=utf8mb4", encoding = 'utf8' ,
                   pool_size=20,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

# 아이디 목록 리스트 만드는 과정
# id_query = """select EPOPCON_ID
# from MEUMS_COMP_REVISIT
# where CNT>300
# """
#
# id_list = pd.read_sql_query(id_query, engine)
# id_list.to_pickle('id')


id_list = pd.read_pickle('id')['EPOPCON_ID']

# 아웃라이어 비율 계산
all_size, out_size = [1, 1]
app = dash.Dash()

data = pd.read_pickle('result_all')
app.layout = html.Div([

    html.Div([
        dcc.Dropdown(
            id='select_id',
            options=[({'label': ids, 'value': ids}) for ids in id_list],
            value=id_list[0]
        ),
        dcc.Dropdown(
            id='select_time',
            options=[{'label': 'day', 'value': 'day'}, {'label': 'night', 'value': 'night'}],
            value='day'
        ),

        dcc.Dropdown(
            id='select_term',
            options=[{'label': '최근 일주일', 'value': 'week'}, {'label': '최근 한달', 'value': 'month'},
                     {'label': '최근 일년', 'value': 'year'}, {'label': '전 체', 'value': 'all'}],
            value='all'
        ),
    ], style={'width': '300'}),

    html.Button(id='submit-button', n_clicks=0, children='Submit', style={'fontSize': 15, 'height': 30}),

    html.Div([
        dcc.Graph(id='feature-graphic')
    ]
    )

])

@app.callback(
    Output('feature-graphic', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('select_id', 'value'),   # id 선택
     State('select_time', 'value'), # 기간 선택(최근 1주일~1년)
     State('select_term', 'value')])    # 시간대 선택(낮, 밤)
def update_graph(n_clicks, select_id, select_time, select_term):
    global all_size, out_size

    if select_time == 'night': time = 'not'

    if select_term == 'week' : date=' and DEAL_DT > date_add(now(), interval -7 day)'
    elif select_term == 'month' : date=' and DEAL_DT > date_add(now(), interval -1 month)'
    elif select_term == 'year' : date=' and DEAL_DT > date_add(now(), interval -1 year)'

    data_query = """
    select MEUMS_COMPANY.LATITUDE, MEUMS_COMPANY.LONGITUDE
    from MEUMS_COMPANY join MEUMS_COMP_REVISIT_HIS on MEUMS_COMPANY.ID = MEUMS_COMP_REVISIT_HIS.COMPANY_ID
    where EPOPCON_ID = '{}'{} and hour(DEAL_DT)
    """.format(select_id, date)

    data=pd.read_sql_query(data_query, engine)
    # feature = pd.read_sql_query(data_query, engine)[['LATITUDE', 'LONGITUDE']]
    feature = data[['LATITUDE', 'LONGITUDE']]
    if len(feature)==0:
        return {
            'data' : go.Scattergeo(),
            'layout': {
                    'title' : 'Out rate : {}%'.format(round(out_size/all_size*100, 2)),
                    'geo': {
                        'scope': 'korea',
                        'lonaxis': {
                            'range': [124, 129]
                        },
                        'lataxis': {
                            'range': [35, 40]
                        },
                    },
                    'height': 1000
                }}

    model = DBSCAN(eps=0.2, min_samples=max(3, len(feature) // 100))       # dpscan의 Epsilon은 임의의 상수로 지정하였고, minPts는 최소 3인 방문기록에 비례한 값을 사용

    predict = pd.DataFrame(model.fit_predict(feature))
    predict.columns = ['predict']
    r = pd.concat([feature, predict], axis=1)

    all_size = len(r)
    out_size = len(r[r.predict == -1])
    return {
        'data': [go.Scattergeo(
            lon=r[r.predict == cluster]['LONGITUDE'],
            lat=r[r.predict == cluster]['LATITUDE'],
            mode='markers',
            name=str(cluster) + '(' + str(len(r[r.predict == cluster])) + ')') for cluster in sorted(r['predict'].unique())],

        'layout': {
            'title' : 'Out rate : {}%'.format(round(out_size/all_size*100, 2)),
            'geo': {
                'scope': 'korea',
                'lonaxis': {
                    'range': [124, 129]
                },
                'lataxis': {
                    'range': [35, 40]
                },

            },
            'height': 1000
        }
    }


if __name__ == '__main__':
    app.run_server(debug=True)