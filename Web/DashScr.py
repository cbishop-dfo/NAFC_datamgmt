import dash
import dash_table
import pandas as pd
import sqlite3
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output


# Read database into dataframe
con = sqlite3.connect("CNV.db")
df = pd.read_sql_query("SELECT * from Casts", con)

# Make a copy of the database to freely manipulate.
dff = df.copy()

# replace any empty strings with null values then drop columns that are completely null
for col in dff:
    dff[col] = dff[col].replace('', np.nan).dropna()
dff = dff.dropna(how='all', axis=1)
del dff["Encoding"]
del dff["Contact"]
del dff["Language"]
del dff["MaintenanceContact"]

app = dash.Dash(__name__)
server = app.server
app.title = "DFO | CTD Meta Data"

theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# Create the app layout
app.layout = html.Div([
    'Ship Number: ',
    dcc.Input(
        id='shipNumber',
        type='text',
        value=""
    ),
    'Trip: ',
    dcc.Input(
        id='trip',
        type='text',
        value=""
    ),
    'Station: ',
    dcc.Input(
        id='station',
        type='text',
        value=""
    ),
    'Latitude: ',
    dcc.Input(
        id='lat',
        type='text',
        value=""
    ),
    'Longitude: ',
    dcc.Input(
        id='lon',
        type='text',
        value=""
    ),
    'Date: ',
    dcc.Input(
        id='date',
        type='text',
        value=""
    ),
    html.Br(),

    html.Div(id="cont", children=[]),

    html.Br(),

    dash_table.DataTable(
        id='table',
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

])


@app.callback(
    Output('table', 'data'),
    Input('shipNumber', "value"),
    Input('trip', "value"),
    Input('station', "value"),
    Input('lat', "value"),
    Input('lon', "value"),
    Input('date', "value"))
def update_table(shpSelected,tripSelected, stationSelected, lat, lon, date):
    print("Ship Number: " + shpSelected.__str__())
    print("Trip: " + tripSelected.__str__())
    print("Station: " + stationSelected.__str__())
    print("\n")
    tempdf = df.copy()
    if not shpSelected == "":
        print("running")
        tempdf = dff[dff["Ship"] == shpSelected.__str__()]
    if not tripSelected == "":
        tempdf = tempdf[tempdf["Trip"] == tripSelected.__str__()]
    if not stationSelected == "":
        tempdf = tempdf[tempdf["Station"] == stationSelected.__str__()]
    if not lat == "":
        tempdf = tempdf[tempdf["Latitude"].str.contains(lat.__str__())]
    if not lon == "":
        tempdf = tempdf[tempdf["Longitude"].str.contains(lon.__str__())]
    if not date == "":
        tempdf = tempdf[tempdf["CastDatetime"].str.contains(date.__str__())]

    return tempdf.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)


