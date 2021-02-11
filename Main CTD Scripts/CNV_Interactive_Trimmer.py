exec(open("C:\QA_paths\set_QA_paths.py").read())
import os
from Toolkits import dir_tk
from Toolkits import cnv_tk
import pandas as pd

def TrimData(cast, df):
    # If you want, you can create a new dataframe and return it at the end. Or edit the existing one, up to you.
    trimmed_df = pd.DataFrame()

    # TODO: Create UI to trim the dataframe
    # Here we want a UI that plots the data and allows the user to use mouse listeners with the plot to select data
    # to be trimmed off.
    # Additionally the data points should change color when deleted so we can see where data was deleted from.
    # We also want to create a selection box, so when a user is holding left click it will draw a box of selected
    # points over the plot.

    # return a dataframe to be passed into cnv_write at the end of main().
    return trimmed_df

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    # Opens file selector UI
    files = dir_tk.confirmSelection()
    for f in files:
        # changes Dir back to original after writing to sub folder
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)

            # Creates Cast object
            cast = cnv_tk.Cast(datafile)

            # Populates Cast Variables
            cnv_tk.cnv_meta(cast, datafile)

            # Creates a pandas dataframe from data in the Cast object
            df = cnv_tk.cnv_to_dataframe(cast)

            # TODO: Create method to trim the dataframe
            trim_df = TrimData(cast, df)

            # Last call would most likely be cnv_write()
            # Used to rewrite a cnv file, for trimming maybe just pass in new dataframe as second parameter, ext= can be
            # whatever file extention you want, can use ".Trimmed" for testing
            # (I believe the final version will have the same file extension as the original file, so ext="")
            cnv_tk.cnv_write(cast, trim_df, ext=".Trimmed")