from Toolkits import cnv_tk
from Toolkits import dir_tk
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.getListOfFiles(dirName)
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)

            # df_press_depth creates a dataframe with both pressure and depth
            df = cnv_tk.df_press_depth(cast)

            # StandardizedDF takes an existing dataframe and returns a df with converted column names to match Midlayer.
            sdf = cnv_tk.StandardizedDF(cast, df)

            # Creates Binned df for Igoss
            sigdf = cnv_tk.cnv_sig_dataframe(cast)
            #cnv_tk.cnv_igoss(cast, sigdf)

            x = sdf["Depth"]
            y = sdf["Temperature"]
            a = sigdf["Depth"]
            b = sigdf["Temperature"]


            fig = go.Figure()

            # Add traces
            fig.add_trace(go.Scatter(x=sdf["Temperature"], y=sdf["Depth"],
                                     mode='markers',
                                     name='All Depths'))
            fig.add_trace(go.Scatter(x=sigdf["Temperature"], y=sigdf["Depth"],
                                     mode='lines+markers',
                                     name='Selected Depths'))


            fig.show()


            print()



