import cnv_tk
import dir_tk
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

    if fileExists:
        with open('CNV_META.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([datafile, cast.Latitude,cast.Longitude, cast.CastDatetime, cast.Instrument, cast.comment])
            print(datafile)

    elif not fileExists:
        with open('CNV_META.csv', 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Filename", "Latitude", "Longitude", "Time", "SerialNumber", "Comments"])
            writer.writerow([datafile, cast.Latitude, cast.Longitude, cast.CastDatetime, cast.Instrument, cast.comment])
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



