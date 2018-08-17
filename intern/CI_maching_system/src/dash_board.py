
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from sqlalchemy import create_engine
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt

engine = create_engine("mysql+pymysql://eums:eums00!q@133.186.146.142:3306/eums-poi?charset=utf8mb4", encoding = 'utf8' ,
                       pool_size=20,pool_recycle=3600,connect_args={'connect_timeout':1000000} )

app = dash.Dash()

query = '''
select *
from TEMP0002
where state = "-1" '''

df = pd.read_sql_query(query, engine)
id_list = [id for id in df['ID']]
app.layout = html.Div([

    html.Button(id='submit-button', n_clicks=0, children='업데이트', style={'fontSize': 15, 'height': 30}),

    html.Div([dt.DataTable(rows=[{}], id='inner_table')], id='table', className="container",
             style={'width': "100%", 'display': 'inline-block'})

])


@app.callback(
    Output('table', 'children'),
    [Input('submit-button', 'n_clicks')])
def get_table(n_clicks):
    return dt.DataTable(
        rows=df.to_dict('records'),
        columns=df.columns,
        row_selectable=True,
        filterable=True,
        sortable=True,
        editable={'ADDR': False, 'ID': False, 'CO_NAME': False, 'LATITUDE': False, 'LONGITUDE': False, 'REP_PHONE_NUM': False, 'STATE': False},
        selected_row_indices=[],
        resizable=True,
        max_rows_in_viewport=10,
        min_width=2000,
        id='inner_table'
    )

if __name__ == '__main__':
    app.run_server(debug=True)