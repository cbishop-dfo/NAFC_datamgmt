import dash
import dash_table
import pandas as pd
import sqlite3
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

con = sqlite3.connect("CNV.db")
df = pd.read_sql_query("SELECT * from Casts", con)


app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
)

if __name__ == '__main__':
    app.run_server(debug=True)