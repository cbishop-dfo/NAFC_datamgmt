import sys
from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import datetime
import time as tt
import numpy as np
import pandas as pd

try:
    import netCDF4 as nc
except:
    pass
"""
Script that takes a cnv file bins the data and writes out a netcdf file

*IMPORTANT: Scan need to be the first column in the dataframe/datafile in order for modifyDF function to remove upcast. 

"""


def modifyDF(cast, df):
    # Typically the pressure/depth index
    pressureIndex = 1
    for row in cast.InstrumentInfo:
        if row.lower().__contains__("pressure") and not cast.isPressure:
            # cast.isPressure = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
        elif row.lower().__contains__("depth") and not cast.isPressure:
            # cast.isPressure = True
            cast.hasDepth = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break

    df = df.astype(float)
    # df['bin'] = pd.cut(df[cast.ColumnNames[pressureIndex]].astype(float), bins)
    # df = df.dropna(axis='rows')
    print("Binning")

    # Here we are dropping any of the upcast values
    lastdepth = 0
    # array to hold the scans to drop *IMPORTANT: Scans need to be the first column in the dataframe
    toDrop = []
    for d in df.values:
        current = float(d[pressureIndex])
        if float(current) > lastdepth:
            lastdepth = current
        else:
            # Append scans to drop, SCAN MUST BE FIRST COLUMN IN DATAFRAME
            toDrop.append(int(d[0]))

    for s in toDrop:
        i = df.loc[df['scan'].astype(float) == float(s)].index
        index = i.values
        df = df.drop(index[0])

    bins = []
    depths = []
    # Create bin with specified intervals and steps
    for i in range(0, 1001, 1):
        bins.append(i + 0.5)

    """
    #bins.append(1000)
    for i in range(1000, 5000, 10):
        bins.append(i)
    """
    count = 0
    for b in bins:
        depths.append(b + 0.5)

        """
        if count < 1001:
            depths.append(b + 0.5)
            count = count + 1
        else:
            nd = b + 5
            depths.append(nd)
            count = count + 1
        """
    # Here we bin all the data and calculate the mean for each bin
    df = df.groupby(pd.cut(df[cast.ColumnNames[pressureIndex]].astype(float), bins)).mean()

    # Had 1 too many values at end
    depths.pop()

    # Create
    # s = df.values.shape[0]
    # newpres = []
    # for s in range(s):
    #    newpres.append(s + 1)

    # Replace mean pressures with bin values
    df[cast.ColumnNames[pressureIndex]] = depths

    # Drop all empty rows
    df = df.dropna(axis=0)

    return df

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
    errorArray = []

    #files = dir_tk.getListOfFiles(dirName)
    files = dir_tk.confirmSelection()
    isbinned = input("Would you like the data to be binned?\nY / N\n")
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        if datafile.lower().endswith(".cnv"):
            try:
                print("Reading: " + datafile)
                cast = cnv_tk.Cast(datafile)
                cnv_tk.cnv_meta(cast, datafile)
                df = cnv_tk.cnv_to_dataframe(cast)
                # df = modifyDF(cast, df)
                # df = cnv_tk.cnv_sig_dataframe(cast)
                if isbinned.lower().__contains__("y"):
                    df = cnv_tk.StandardizedDF(cast,df)
                    df = cnv_tk.BinDF(cast, df)
                outfile = datafile.replace(".cnv", ".nc")
                cnv_tk.NCWrite4(cast, df, nc_outfile=outfile)
                # input("Hold, Press enter to load next file")


            except Exception as e:
                err = [e.__str__(), datafile]
                errorArray.append(err)
                continue

    print("Script Complete\n")
    print("*** List Of Errors ***")
    for er in errorArray:
        print("\nError: " + er[0] + "\nFilename: " + er[1])