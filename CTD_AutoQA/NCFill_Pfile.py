#exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import p_tk
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
            cast = p_tk.Cast(datafile)

            print("Reading: " + datafile)
            # Records the header info
            p_tk.read_pFile(cast, datafile)

            # Records Channel stats from the header
            p_tk.getChannelInfo(cast, datafile)

            # Creates Pandas Dataframe from the pfile
            df = p_tk.pfile_to_dataframe(cast, datafile)

            # Data limit is used alongside database if database is used (you can ignore this in this test example)
            cast.DataLimit = len(df.index)

            # Assigns meta data to the cast object ie: latitude, longitude, Sounder Depth, Meteorological data, ect
            p_tk.pfile_meta(cast, datafile)

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
        cast = p_tk.Cast(datafile)

        print("Reading: " + datafile)
        # Records the header info
        p_tk.read_pFile(cast, datafile)

        # Records Channel stats from the header
        p_tk.getChannelInfo(cast, datafile)

        # Creates Pandas Dataframe from the pfile
        df = p_tk.pfile_to_dataframe(cast, datafile)

        # Data limit is used alongside database if database is used (you can ignore this in this test example)
        cast.DataLimit = len(df.index)

        # Assigns meta data to the cast object ie: latitude, longitude, Sounder Depth, Meteorological data, ect
        p_tk.pfile_meta(cast, datafile)
        for c in colArr:
            if not c in df.columns:
                df[c] = np.nan
        name = cast.ship.__str__() + cast.trip.__str__() + cast.station.__str__() + ".csv"
        df.to_csv(name, index=False)

