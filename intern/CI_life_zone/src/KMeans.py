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
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from sqlalchemy import create_engine
from dash.dependencies import Input, Output, State
import math
from sklearn.cluster import KMeans
from sklearn import mixture
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
# Create a pandas DataFrame from 2010YumaAZ.csv

engine = create_engine("mysql+pymysql://eums:eums00!q@192.168.0.50:3306/eums?charset=utf8mb4", encoding = 'utf8' ,
                   pool_size=20,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

# id_query = """select EPOPCON_ID
# from MEUMS_COMP_REVISIT
# where CNT>300
# """
#
# id_list = pd.read_sql_query(id_query, engine)
# id_list.to_pickle('id')
#

id_list = pd.read_pickle('id')['EPOPCON_ID']
data = pd.read_pickle('result_all')[['EPOPCON_ID', 'LATITUDE', 'LONGITUDE']]
all_size, out_size = [1, 1]
app = dash.Dash()

app.layout = html.Div([

    html.Div([
        dcc.Dropdown(
            id='select_id',
            options=[({'label': ids, 'value': ids}) for ids in id_list],
            value=id_list[0]
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
    [State('select_id', 'value')])
def update_graph(n_clicks, select_id):
    global all_size, out_size
    time = ''
    date = ''

    feature = data[data.EPOPCON_ID==select_id].reset_index()[['LATITUDE', 'LONGITUDE']]
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

    all_size = len(feature)

    model = KMeans(n_clusters=3)
    model.fit(feature)

    predict = pd.DataFrame(model.predict(feature))

    predict.columns = ['predict']
    r = pd.concat([feature, predict], axis=1)

    return {
        'data': [go.Scattergeo(
            lon=r[r.predict == cluster]['LONGITUDE'],
            lat=r[r.predict == cluster]['LATITUDE'],
            mode='markers',
            name=str(cluster) + '(' + str(len(r[r.predict == cluster])) + ')') for cluster in sorted(r['predict'].unique())],
        'layout': {
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