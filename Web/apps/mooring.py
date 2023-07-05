#exec(open("C:\QA_paths\set_QA_paths.py").read())


import dash
import dash_table
import pandas as pd
import sqlite3
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dcc import Download
# from dash_extensions import Download

import numpy as np
from dash.dependencies import Input, Output
from Toolkits import cnv_tk

try:
    moordf = pd.read_excel("assets//Mooring Summary.xlsx")
except:
    try:
        moordf = pd.read_csv("assets/Mooring Summary.xlsx")
    except Exception as e:
        print(e.__str__())


def ReadMooring(df):
    index = 0
    depindex = 0
    recindex = 0
    toBeDeployedIndex = 0
    MoorLostIndex = 0
    for row in df.values:
        if row[0] == "Moorings Recovered":
            depindex = index

        elif row[0] == "Moorings To Be Deployed":
            toBeDeployedIndex = index

        elif row[0] == "Moorings Lost":
            MoorLostIndex = index

        index = index + 1

    dep = df.iloc[:depindex]
    dep = dep.iloc[1::2, :]

    rec = df.iloc[depindex+1:toBeDeployedIndex]
    rec = rec.iloc[0::2, :]

    tbd = df.iloc[toBeDeployedIndex+1:MoorLostIndex]
    tbd = tbd.iloc[0::2, :]

    mlost = df.iloc[MoorLostIndex+1:]
    mlost = mlost.iloc[0::2, :]

    dep["Status"] = "Mooring Deployed"
    rec["Status"] = "Mooring Recovered"
    tbd["Status"] = "To Be Deployed"
    mlost["Status"] = "Mooring Lost"

    result = pd.concat([dep, rec, tbd, mlost], ignore_index=True)

    return result


# # replace any empty strings with null values then drop columns that are completely null
# for col in dff:
#     dff[col] = dff[col].replace('', np.nan).dropna()
# dff = dff.dropna(how='all', axis=1)

app = dash.Dash(__name__)
server = app.server
app.title = "DFO | Biomass Data"

try:
    moordf = ReadMooring(moordf)


    theme =  {
        'dark': True,
        'detail': '#007439',
        'primary': '#00EA64',
        'secondary': '#6E6E6E',
    }
    #biodf["Set"] = str(i).zfill(3) for i in biodf["Set"].values()

    # Create the app layout
    #app.layout = html.Div([
    layout = html.Div([
        dbc.Row(
            dbc.Col(
                dbc.CardHeader("Mooring Data"),
                        width={'size': 12, 'offset': 0},
                ),
        ),

        html.Br(),
            dcc.Input(
            placeholder='Mooring',
            id='mooring',
            type='text',
            value="",
            persistence=True,
            persistence_type="memory"
        ),
        dcc.Input(
            placeholder='Mooring Number',
            id='moornum',
            type='text',
            value="",
            persistence=True,
            persistence_type="memory"
        ),
        dcc.Input(
            placeholder='Instruments',
            id='inst',
            type='text',
            value="",
            persistence=True,
            persistence_type="memory"
        ),
        dcc.Input(
            placeholder='Date In',
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
        dcc.Input(
            placeholder='Comment',
            id='comment',
            type='text',
            value="",
            persistence=True,
            persistence_type="memory"
        ),
        dcc.Input(
            placeholder='Status',
            id='status',
            type='text',
            value="",
            persistence=True,
            persistence_type="memory"
        ),
        html.Hr(),
        #html.Button("Download", id="btn"), Download(id="download"),

        html.Br(),

        html.Div(id="cont", children=[]),

        html.Br(),
        html.Div(id='container-button-timestamp'),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable
                (
                    id='table_mooring',
                    columns=[{"name": i, "id": i} for i in moordf.columns],
                    data=moordf.to_dict('records'),

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
except Exception as e:
    print(e.__str__())

if __name__ == '__main__':
    app.run_server(debug=True)


