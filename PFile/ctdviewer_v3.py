import os
import pandas as pd
from Toolkits import p_tk
from Toolkits import dir_tk
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def loaddata(datafile):
    # Creates the cast object
    cast = p_tk.Cast(datafile)

    # Records the header info
    p_tk.read_pFile(cast, datafile)

    # Records Channel stats from the header
    p_tk.getChannelInfo(cast, datafile)

    # Creates Pandas Dataframe from the pfile
    df = p_tk.pfile_to_dataframe(cast, datafile)

    # Assigns meta data to the cast object ie: latitude, longitude, Sounder Depth, Meteorological data, ect
    p_tk.pfile_meta(cast, datafile)

    return [cast, df]

def plotVertical(cast, df):
    # Vertical CTD
    fig = px.scatter(df, x="temp", y="pres")
    fig.update_layout(title_text="Vertical CTD Plot | Datafile: " + filename)
    fig['layout']['xaxis']['title'] = 'Temperature'
    fig['layout']['yaxis']['title'] = 'Pressure'
    fig.show()

def plotTowed(cast, df):
    # Towed CTD
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Temperature Over Time', 'Pressure Over Time'))
    fig.add_trace(
        go.Scatter(x=df["scan"], y=df["temp"]),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["scan"], y=df["pres"]),
        row=1, col=2

    )
    fig.update_layout(height=720, width=1280, title_text="Towed CTD Plot | Datafile: " + filename)
    fig['layout']['xaxis']['title'] = 'Time'
    fig['layout']['xaxis2']['title'] = 'Time'
    fig['layout']['yaxis']['title'] = 'Temperature'
    fig['layout']['yaxis2']['title'] = 'Pressure'
    fig.show()

########################################################################################
# MAIN PART OF PROGRAM
########################################################################################
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
    pd.options.plotting.backend = "plotly"

    #files = dir_tk.getListOfFiles(dirName)
    files = dir_tk.confirmSelection()
    for file in files: #sorted(glob.glob('*.p[0-9][0-9][0-9][0-9]')):
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = file.name
        data = loaddata(datafile)
        filename = datafile.split("/")
        filename = filename[filename.__len__() - 1]
        cast = data[0]
        df = data[1]
        df.columns = df.columns.str.lower()
        if filename.__contains__(".D"):
            # Convert Dfile
            df = p_tk.depthDF_to_PresDF(cast, df)

        if cast.castType.upper() == "V":
            plotVertical(cast, df)
        elif cast.castType.upper() == "T":
            plotTowed(cast, df)
        else:
            print("No Cast Type Provided in file...\nPlotting Towed and Vertical")
            plotVertical(cast, df)
            plotTowed(cast, df)

        print("Plotting " + datafile.__str__())

