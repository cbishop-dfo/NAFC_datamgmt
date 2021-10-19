import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import sqlite3
import pandas as pd
import dash
# Connect to main app.py file
from app import app
import numpy as np
from app import server
import dash_bootstrap_components as dbc
from Toolkits import cnv_tk
# Connect to your app pages
from apps import cnvapp
from apps import bio
from apps import azmp
from apps import elog
import assets
import zipfile
from dash_extensions.snippets import send_data_frame


### Dataframe imports ##################################################################################
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

try:
    econ = sqlite3.connect("assets//ELOG.db")
    elog_database = "assets//ELOG.db"
except:
    try:
        econ = sqlite3.connect("assets/ELOG.db")
        elog_database = "assets/ELOG.db"
    except:
        econ = sqlite3.connect("ELOG.db")
        elog_database = "ELOG.db"

try:
    azmpdf = pd.read_csv("assets//NEW_AZMP_Bottle_Data.csv")
except:
    azmpdf = pd.read_csv("assets/NEW_AZMP_Bottle_Data.csv")

try:
    biodf = pd.read_csv("assets//NEWBIOMASS.csv")
except:
    biodf = pd.read_csv("assets/NEWBIOMASS.csv")

df = pd.read_sql_query("SELECT * from Casts", con)
data = pd.read_sql_query("SELECT * from Data", con)
mergedDF = df.merge(data, left_on='id', right_on='cid')
# Make a copy of the database to freely manipulate.
dff = df.copy()
elogdf = pd.read_sql_query("SELECT * from ELOG", econ)
tempdf = []

# replace any empty strings with null values then drop columns that are completely null
for col in dff:
    dff[col] = dff[col].replace('', np.nan).dropna()
dff = dff.dropna(how='all', axis=1)
# Remove columns we don't want to see in the table
del dff["Encoding"]
del dff["Contact"]
del dff["Language"]
del dff["MaintenanceContact"]

# Splitting Ship_Trip_Stn for AZMP file into separate columns
azmpdf["Ship"] = azmpdf["Ship_Trip_Stn"].astype(str).str[0:2]
azmpdf["Trip"] = azmpdf["Ship_Trip_Stn"].astype(str).str[2:5]
azmpdf["Station Number"] = azmpdf["Ship_Trip_Stn"].astype(str).str[5:8]

# Splitting Seq_number for ELOG DB into separate columns
elogdf["Ship Name"] = elogdf["Seq_Number"].str[0:4]
elogdf["Trip"] = elogdf["Seq_Number"].str[4:7]
elogdf["Station Number"] = elogdf["Seq_Number"].str[13:]


mergedDF = dff.merge(data, left_on='id', right_on='cid')
logo = "https://www.canada.ca/etc/designs/canada/wet-boew/assets/sig-blk-en.svg"
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    #dbc.Col(html.Img(src=logo, height="30px", style={'textAlign': 'center'})),
    html.Div([
        html.Img(
            src=logo,
            style={
                'height': '50%',
                'width': '50%'
            })
    ], style={'textAlign': 'center', "margin-top": "25px", "margin-bottom": "25px"}),
    dbc.Navbar(
        [
            dbc.NavLink("CNV", href="/apps/cnvapp"),
            dbc.NavLink("AZMP", href="/apps/azmp"),
            dbc.NavLink("BIO", href="/apps/bio"),
            dbc.NavLink("ELOG", href="/apps/elog"),

        ],
        color="#263152",
        dark=True
    ),
    html.Div(id='page-content', children=[])
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/cnvapp':
        return cnvapp.layout
    if pathname == '/apps/bio':
        return bio.layout
    if pathname == '/apps/azmp':
        return azmp.layout
    if pathname == '/apps/elog':
        return elog.layout
    else:
        #return "404 Page Error! Please choose a link"
        return cnvapp.layout

### CNV ###################################################################################################
"""
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
"""
###
@app.callback(
    Output('table_cnv', 'data'),
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
        tempdf = tempdf[tempdf["Ship"] == shpSelected.__str__()]
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

### AZMP ##################################################################################################
@app.callback(
    Output('table_azmp', 'data'),
    Input('shipNumber', "value"),
    Input('trip', "value"),
    Input('station', "value"),
    Input('lat_min', "value"),
    Input('lat_max', "value"),
    Input('lon_min', "value"),
    Input('lon_max', "value"),
    Input('date', "value"))
def update_table(shpSelected,tripSelected, stationSelected, lat_min, lat_max, lon_min, lon_max, date):
    #print("Ship Number: " + shptrpSelected.__str__())
    #print("Trip: " + stsSelected.__str__())
    #print("Station: " + stationSelected.__str__())
    #print("\n")
    tempdf = azmpdf.copy()
    tempdf["Latitude"] = tempdf["Latitude"].astype(float)
    tempdf["Longitude"] = tempdf["Longitude"].astype(float)
    if not shpSelected == "":
        tempdf = tempdf[tempdf["Ship"] == shpSelected.__str__()]
    if not tripSelected == "":
        tempdf = tempdf[tempdf["Trip"] == tripSelected.__str__()]
    if not stationSelected == "":
        tempdf = tempdf[tempdf["Station Number"] == stationSelected.__str__()]
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
        tempdf = tempdf[tempdf["Date"].str.contains(date.__str__())]

    return tempdf.to_dict('records')
### BIO ###################################################################################################
@app.callback(
    Output('table_bio', 'data'),
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
    tempdf = biodf.copy()
    tempdf["Lat"] = tempdf["Lat"].astype(float)
    tempdf["Lon"] = tempdf["Lon"].astype(float)
    tempdf["Ship"] = tempdf["Ship"]
    tempdf["Trip"] = tempdf["Trip"]
    tempdf["Set"] = tempdf["Set"]

    if not shpSelected == "":
        tempdf = tempdf[tempdf["Ship"] == int(shpSelected)]
    if not tripSelected == "":
        tempdf = tempdf[tempdf["Trip"] == int(tripSelected)]
    if not stationSelected == "":
        tempdf = tempdf[tempdf["Set"] == int(stationSelected)]
    if not lat_min == "" and not lat_min == "-":
        if not lat_max == "" and not lat_max == "-":
            tempdf = tempdf[tempdf["Lat"].astype(float).between(float(lat_min), float(lat_max))]
        else:
            # If no max is set only look for min value
            tempdf = tempdf[tempdf["Lat"].astype(float).between(float(lat_min), float(lat_min))]
    if not lon_min == "" and not lon_min == "-":
        if not lon_max == "" and not lon_max == "-":
            tempdf = tempdf[tempdf["Lon"].astype(float).between(float(lon_min), float(lon_max))]
        else:
            # If no max is set only look for min value
            tempdf = tempdf[tempdf["Lon"].astype(float).between(float(lon_min), float(lon_min))]
    if not date == "":
        tempdf = tempdf[tempdf["Date"].str.contains(date.__str__())]

    return tempdf.to_dict('records')
########################################################################################################
@app.callback(
    Output("download", "data"),
    Input("btn", "n_clicks"),
    Input('shipNumber', "value"),
    Input('trip', "value"),
    Input('station', "value"),
    Input('lat_min', "value"),
    Input('lat_max', "value"),
    Input('lon_min', "value"),
    Input('lon_max', "value"),
    Input('date', "value"))
def downloadTable(clicks,shpSelected,tripSelected, stationSelected, lat_min, lat_max, lon_min, lon_max, date):
    print("Ship Number: " + shpSelected.__str__())
    print("Trip: " + tripSelected.__str__())
    print("Station: " + stationSelected.__str__())
    #print("Clicks: \n" + clicks)
    Filename = ""
    if clicks != None:
        tempdf = biodf.copy()
        tempdf["Lat"] = tempdf["Lat"].astype(float)
        tempdf["Lon"] = tempdf["Lon"].astype(float)
        tempdf["Ship"] = tempdf["Ship"]
        tempdf["Trip"] = tempdf["Trip"]
        tempdf["Set"] = tempdf["Set"]

        if not shpSelected == "":
            tempdf = tempdf[tempdf["Ship"] == int(shpSelected)]
            Filename = Filename + shpSelected.__str__()
        if not tripSelected == "":
            tempdf = tempdf[tempdf["Trip"] == int(tripSelected)]
            Filename = Filename + tripSelected.__str__()
        if not stationSelected == "":
            tempdf = tempdf[tempdf["Set"] == int(stationSelected)]
            Filename = Filename + stationSelected.__str__()
        if not lat_min == "" and not lat_min == "-":
            if not lat_max == "" and not lat_max == "-":
                tempdf = tempdf[tempdf["Lat"].astype(float).between(float(lat_min), float(lat_max))]
            else:
                # If no max is set only look for min value
                tempdf = tempdf[tempdf["Lat"].astype(float).between(float(lat_min), float(lat_min))]
        if not lon_min == "" and not lon_min == "-":
            if not lon_max == "" and not lon_max == "-":
                tempdf = tempdf[tempdf["Lon"].astype(float).between(float(lon_min), float(lon_max))]
            else:
                # If no max is set only look for min value
                tempdf = tempdf[tempdf["Lon"].astype(float).between(float(lon_min), float(lon_min))]

        if not date == "":
            tempdf = tempdf[tempdf["Date"].str.contains(date.__str__())]

        clicks = None
        Filename = Filename + ".xls"
        return send_data_frame(tempdf.to_excel, Filename)

    else:
        print("not clicked")





########################################################################################################

if __name__ == '__main__':
    app.run_server(debug=True)
    app.config['suppress_callback_exceptions'] = True
