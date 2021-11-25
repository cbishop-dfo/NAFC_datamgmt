exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import cnv_tk
from Toolkits import dir_tk
import numpy as np
import os

""" 
Script takes all cnv files in a directory, creates a list of unique data columns and fills dataframes missing unique
columns with nans.
"""
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.confirmSelection(dirName)

    colArr = []

    # First loop to get all data columns
    for f in files:
        # changes Dir back to original
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f


        try:
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            for c in df:
                if not c in colArr:
                    colArr.append(c)
        except Exception as e:
            x = input("ERROR: " + e.__str__() + "\nProgram Halted!\nPress Enter To Continue...")

    for f in files:
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        print(datafile)
        cast = cnv_tk.Cast(datafile)
        cnv_tk.cnv_meta(cast, datafile)
        name = cast.ship.__str__() + cast.trip.__str__() + cast.station.__str__() + ".csv"
        df = cnv_tk.cnv_to_dataframe(cast)
        for c in colArr:
            if not c in df.columns:
                df[c] = np.nan
        #df.to_csv(name, index=False)

