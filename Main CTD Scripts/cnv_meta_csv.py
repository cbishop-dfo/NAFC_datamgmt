from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import csv
import datetime
import time as tt
import numpy as np
import xarray
import pandas as pd
import sqlite3

def writeMetaToCNV(cast, df):


    fileExists = False
    for f in files:
        if f == 'CNV_META.csv':
            fileExists = True
    row = [datafile, cast.ship, cast.trip, cast.station, cast.Latitude, cast.Longitude, cast.CastDatetime, cast.Instrument, cast.SounderDepth, cast.SamplingRate, cast.comment]
    if fileExists:
        with open('CNV_META.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(row)
            print(datafile)

    elif not fileExists:
        with open('CNV_META.csv', 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Filename", "Ship", "Trip", "Station", "Latitude", "Longitude", "Datetime", "SerialNumber", "Sounder Depth", "Sample Size", "Comments"])
            writer.writerow(row)
            files.append('CNV_META.csv')




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
            df = cnv_tk.cnv_to_dataframe(cast)
            writeMetaToCNV(cast,df)



