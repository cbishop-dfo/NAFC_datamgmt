exec(open("C:\QA_paths\set_QA_paths.py").read())


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

theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

# Create the app layout
app.layout = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.CardHeader("CTD Meta Data"),
                    width={'size': 12, 'offset': 0},
            ),
    ),

    html.Br(),
    'Ship Number: ',
    dcc.Input(
        id='shipNumber',
        type='text',
        value=""
    ),
    ' Trip: ',
    dcc.Input(
        id='trip',
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
    dcc.Checklist(
    options=[
        {'label': 'CTD', 'value': 'CTD'},
        {'label': 'Biological', 'value': 'BIO'}
    ],
    value=[],
    labelStyle={'display': 'inline-block'}
),
    html.Hr(),
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

        ),
    ),
])

@app.callback(Output('container-button-timestamp', 'children'),
              Input('igoss', 'n_clicks'),
              Input('simple', 'n_clicks'),
              Input('cnv', 'n_clicks'),
              Input('shipNumber', "value"),
              Input('trip', "value"),
              Input('station', "value"),
              Input('lat_min', "value"),
              Input('lat_max', "value"),
              Input('lon_min', "value"),
              Input('lon_max', "value"),
              Input('date', "value")

)
def writeFiles(ig, net, cv, shpSelected,tripSelected, stationSelected, lat_min, lat_max, lon_min, lon_max, date):
    sql_to_df = pd.DataFrame()
    cast = cnv_tk.Cast()
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    tempdf = df.copy()
    tempdf["Latitude"] = tempdf["Latitude"].astype(float)
    tempdf["Longitude"] = tempdf["Longitude"].astype(float)
    if not shpSelected == "":
        print("running")
        tempdf = dff[dff["Ship"] == shpSelected.__str__()]
    if not tripSelected == "":
        tempdf = tempdf[tempdf["Trip"] == tripSelected.__str__()]
    if not stationSelected == "":
        tempdf = tempdf[tempdf["Station"] == stationSelected.__str__()]
    if not lat_min == "" and not lat_min == "-":
        if not lat_max == "" and not lat_max == "-":
            tempdf = tempdf[tempdf["Latitude"].astype(float).between(float(lat_min), float(lat_max))]
        else:
            # If no max is set only look for min value
            tempdf = tempdf[tempdf["Latitude"].astype(float).between(float(lat_min), float(lat_min))]
    if not lon_min == "" and not lon_min == "-":
        if not lon_max == "" and not lon_max == "-":
            tempdf = tempdf[tempdf["Longitude"].astype(float).between(float(lon_min), float(lon_max))]
        else:
            # If no max is set only look for min value
            tempdf = tempdf[tempdf["Longitude"].astype(float).between(float(lon_min), float(lon_min))]
    if not date == "":
        tempdf = tempdf[tempdf["CastDatetime"].str.contains(date.__str__())]

    # Creates and returns cast object and dataframe from database
    def DatabaseFetch(c, sql_to_df):
        conn = sqlite3.connect(database)

        # Cast id
        cid = c[0]
        # Data limit
        # dlmt = c[25]
        dlmt = c[c.__len__()-1]
        sql_to_df = pd.read_sql_query(
            "select * from Data where Data.cid = (Select id from Casts where id = '{dv}') limit '{lmt}'".format(
                dv=cid, lmt=dlmt),
            conn)
        del sql_to_df["cid"]
        del sql_to_df["did"]
        # Populate cast variables from database object.
        cast = cnv_tk.Cast()
        cast.id = c[0]
        cast.ShipName = c[1]
        cast.ship = c[2]
        cast.trip = c[3]
        cast.station = c[4]
        cast.Latitude = c[5]
        cast.Longitude = c[6]
        cast.SounderDepth = c[7]
        cast.Instrument = c[8]
        cast.InstrumentName = c[9]
        cast.comment = c[10]
        cast.CastDatetime = c[11]
        cast.File = c[12]
        cast.Country = c[13]
        cast.OrgName = c[14]
        cast.DataLimit = c[15]
        cast.datafile = cast.File
        cur = conn.cursor()
        # Get Header Data
        cur.execute(
            "select * from Header where Header.cid = (Select id from Casts where id = '{dv}')".format(dv=cid))
        header = cur.fetchall()
        for h in header:
            cast.header.append(h[2])
            cast.userInput.append(h[2])
        # Get Software Data
        cur.execute(
            "select * from Software where Software.cid = (Select id from Casts where id = '{dv}')".format(dv=cid))
        software = cur.fetchall()
        for s in software:
            cast.software.append(s[2])
        # Get Instrument Data
        cur.execute(
            "select * from Instrument where Instrument.cid = (Select id from Casts where id = '{dv}')".format(
                dv=cid))
        instrument = cur.fetchall()
        for i in instrument:
            cast.InstrumentInfo.append(i[2])
        # replace any empty strings with null values then drop columns that are completely null
        for col in sql_to_df:
            sql_to_df[col] = sql_to_df[col].replace('', np.nan).dropna()
        sql_to_df = sql_to_df.dropna(how='all', axis=1)
        return [cast, sql_to_df]


    if 'igoss' in changed_id:
        msg = 'Writing IGOSS'
        print(msg)
        for c in tempdf.values:
            fetch = DatabaseFetch(c, sql_to_df)
            cast = fetch[0]
            sql_to_df = fetch[1]
            cast.data = sql_to_df.values.tolist()

            # Creates Binned df for Igoss
            sigdf = cnv_tk.cnv_sig_dataframe(cast)

            # Writes IGOSS File
            cnv_tk.cnv_igoss(cast, sigdf)

    elif 'simple' in changed_id:
        msg = 'Writing Simple CNV'
        print(msg)
        for c in tempdf.values:
            fetch = DatabaseFetch(c, sql_to_df)
            cast = fetch[0]
            sql_to_df = fetch[1]
            cnv_tk.cnv_write_simple(cast, sql_to_df)
    elif 'simple' in changed_id:
        msg = 'NETCDF Writer Status: WIP'
        print(msg)
        for c in tempdf.values:
            fetch = DatabaseFetch(c, sql_to_df)
            cast = fetch[0]
            sql_to_df = fetch[1]
            # Call NETCDF writer function here.
    elif 'cnv' in changed_id:
        msg = 'Writing CNV'
        print(msg)
        for c in tempdf.values:
            fetch = DatabaseFetch(c, sql_to_df)
            cast = fetch[0]
            sql_to_df = fetch[1]
            # Writes CNV file as the original.
            cnv_tk.cnv_write(cast, sql_to_df, ext="")

    else:
        msg = ''
    return html.Div(msg)

@app.callback(
    Output('table', 'data'),
    Input('shipNumber', "value"),
    Input('trip', "value"),
    Input('station', "value"),
    Input('lat_min', "value"),
    Input('lat_max', "value"),
    Input('lon_min', "value"),
    Input('lon_max', "value"),
    Input('date', "value"))
def update_table(shpSelected,tripSelected, stationSelected, lat_min, lat_max, lon_min, lon_max, date):
    print("Ship Number: " + shpSelected.__str__())
    print("Trip: " + tripSelected.__str__())
    print("Station: " + stationSelected.__str__())
    print("\n")
    tempdf = df.copy()
    tempdf["Latitude"] = tempdf["Latitude"].astype(float)
    tempdf["Longitude"] = tempdf["Longitude"].astype(float)
    if not shpSelected == "":
        tempdf = dff[dff["Ship"] == shpSelected.__str__()]
    if not tripSelected == "":
        tempdf = tempdf[tempdf["Trip"] == tripSelected.__str__()]
    if not stationSelected == "":
        tempdf = tempdf[tempdf["Station"] == stationSelected.__str__()]
    if not lat_min == "" and not lat_min == "-":
        if not lat_max == "" and not lat_max == "-":
            tempdf = tempdf[tempdf["Latitude"].astype(float).between(float(lat_min), float(lat_max))]
        else:
            # If no max is set only look for min value
            tempdf = tempdf[tempdf["Latitude"].astype(float).between(float(lat_min), float(lat_min))]
    if not lon_min == "" and not lon_min == "-":
        if not lon_max == "" and not lon_max == "-":
            tempdf = tempdf[tempdf["Longitude"].astype(float).between(float(lon_min), float(lon_max))]
        else:
            # If no max is set only look for min value
            tempdf = tempdf[tempdf["Longitude"].astype(float).between(float(lon_min), float(lon_min))]
    if not date == "":
        tempdf = tempdf[tempdf["CastDatetime"].str.contains(date.__str__())]

    return tempdf.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)


