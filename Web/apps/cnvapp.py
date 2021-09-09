#exec(open("C:\QA_paths\set_QA_paths.py").read())

import numpy as np
import dash
import dash_table
import pandas as pd
import sqlite3
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from Toolkits import cnv_tk


# Read database into dataframe
try:
    con = sqlite3.connect("assets//CNV.db")
    database = "assets//CNV.db"
except:
    try:
        con = sqlite3.connect("assets/CNV.db")
        database = "assets/CNV.db"
    except:
        con = sqlite3.connect("CNV.db")
        database = "CNV.db"

df = pd.read_sql_query("SELECT * from Casts", con)
data = pd.read_sql_query("SELECT * from Data", con)
mergedDF = df.merge(data, left_on='id', right_on='cid')
# Make a copy of the database to freely manipulate.
dff = df.copy()

# replace any empty strings with null values then drop columns that are completely null
for col in dff:
    dff[col] = dff[col].replace('', np.nan).dropna()
dff = dff.dropna(how='all', axis=1)
# Remove columns we don't want to see in the table
del dff["Encoding"]
del dff["Contact"]
del dff["Language"]
del dff["MaintenanceContact"]

mergedDF = dff.merge(data, left_on='id', right_on='cid')

app = dash.Dash(__name__)
server = app.server
app.title = "DFO | CTD Meta Data"

#theme =  {
#    'dark': True,
#    'detail': '#007439',
#    'primary': '#00EA64',
#    'secondary': '#6E6E6E',
#}

# Create the app layout
#app.layout = html.Div([
layout = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.CardHeader("CTD Meta Data"),
                    width={'size': 12, 'offset': 0},
            ),
    ),

    html.Br(),
    html.Br(),
    dcc.Input(
        placeholder='Ship Number: ',
        id='shipNumber',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    dcc.Input(
        placeholder='Trip',
        id='trip',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    dcc.Input(
        placeholder='Station',
        id='station',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    dcc.Input(
        placeholder='Date',
        id='date',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    html.Br(),
    html.Br(),
    dcc.Input(
        placeholder='Latitude Min',
        id='lat_min',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    dcc.Input(
        placeholder='Latitude Max',
        id='lat_max',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    dcc.Input(
        placeholder='Longitude Min',
        id='lon_min',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    dcc.Input(
        placeholder='Longitude Max',
        id='lon_max',
        type='text',
        value="",
        persistence=True,
        persistence_type="memory"
    ),
    html.Hr(),
    #dcc.Checklist(
    #options=[
    #    {'label': 'CTD', 'value': 'CTD'},
    #    {'label': 'Biological', 'value': 'BIO'}
    #],
    #value=[],
    #labelStyle={'display': 'inline-block'}
    #),
    #html.Hr(),
    html.Button('Write IGOSS', id='igoss', n_clicks=0),
    html.Button('Write NETCDF', id='netcdf', n_clicks=0),
    html.Button('Write Simple CNV', id='simple', n_clicks=0),
    html.Button('Write CNV', id='cnv', n_clicks=0),

    html.Br(),

    html.Div(id="cont", children=[]),

    html.Br(),
    html.Div(id='container-button-timestamp'),
    dbc.Row(
        dbc.Col(
            dash_table.DataTable
            (
                id='table_cnv',
                columns=[{"name": i, "id": i} for i in dff.columns],
                data=dff.to_dict('records'),

                style_cell_conditional=[
                    {
                        'textAlign': 'left'
                    }
                ],
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )

        ),style={"margin-left": "5px"}
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)


