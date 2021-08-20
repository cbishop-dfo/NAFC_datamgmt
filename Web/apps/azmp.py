#exec(open("C:\QA_paths\set_QA_paths.py").read())


import dash
import dash_table
import pandas as pd
import sqlite3
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np
from dash.dependencies import Input, Output
from Toolkits import cnv_tk


# Read database into dataframe
database = "CNV.db"
con = sqlite3.connect(database)
try:
    azmpdf = pd.read_csv("assets//NEW_AZMP_Bottle_Data.csv")
except:
    azmpdf = pd.read_csv("assets/NEW_AZMP_Bottle_Data.csv")

# Make a copy of the database to freely manipulate.
#azmpdfdff = azmpdfdf.copy()

# # replace any empty strings with null values then drop columns that are completely null
# for col in dff:
#     dff[col] = dff[col].replace('', np.nan).dropna()
# dff = dff.dropna(how='all', axis=1)

app = dash.Dash(__name__)
server = app.server
app.title = "DFO | AZMP Bottle Data"

theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# Create the app layout
#app.layout = html.Div([
layout = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.CardHeader("AZMP Bottle Data"),
                    width={'size': 12, 'offset': 0},
            ),
    ),

    html.Br(),
    'Ship Trip: ',
    dcc.Input(
        id='shipTrip',
        type='text',
        value=""
    ),
    ' Ship Trip Stn: ',
    dcc.Input(
        id='sts',
        type='text',
        value=""
    ),
    ' Station: ',
    dcc.Input(
        id='station',
        type='text',
        value=""
    ),
    ' Date: ',
    dcc.Input(
        id='date',
        type='text',
        value=""
    ),
    html.Br(),
    html.Br(),
    ' Latitude Min: ',
    dcc.Input(
        id='lat_min',
        type='text',
        value=""
    ),
    ' Latitude Max: ',
    dcc.Input(
        id='lat_max',
        type='text',
        value=""
    ),
    ' Longitude Min: ',
    dcc.Input(
        id='lon_min',
        type='text',
        value=""
    ),
    ' Longitude Max: ',
    dcc.Input(
        id='lon_max',
        type='text',
        value=""
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
    #html.Button('Write IGOSS', id='igoss', n_clicks=0),
    #html.Button('Write NETCDF', id='netcdf', n_clicks=0),
    #html.Button('Write Simple CNV', id='simple', n_clicks=0),
    #html.Button('Write CNV', id='cnv', n_clicks=0),

    html.Br(),

    html.Div(id="cont", children=[]),

    html.Br(),
    html.Div(id='container-button-timestamp'),
    dbc.Row(
        dbc.Col(
            dash_table.DataTable
            (
                id='table_azmp',
                columns=[{"name": i, "id": i} for i in azmpdf.columns],
                data=azmpdf.to_dict('records'),

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
                },
            )

        ),style={"margin-left": "5px"}
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)


