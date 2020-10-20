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

    # TODO: Change file name to be unique ship+trip_META.csv
    fileExists = False
    for f in files:
        if f == csvName:
            fileExists = True
    id = cast.ship.__str__() + cast.trip.__str__() + cast.station.__str__()
    cid = cast.ship.__str__() + cast.trip.__str__()
    dateinfo = cast.CastDatetime.split()
    date = dateinfo[0]
    time = dateinfo[1]
    year = date.split("-")[2]
    month = date.split("-")[1]
    day = date.split("-")[0]
    row = [datafile, id, cid, cast.ship, cast.trip, cast.station, cast.Latitude, cast.Longitude, cast.CastDatetime, cast.Instrument, cast.SounderDepth, cast.SamplingRate, cast.comment, date, time, year, month, day]
    if fileExists:
        with open(csvName, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(row)

    elif not fileExists:
        with open(csvName, 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Filename", "ID", "Cruise ID", "Ship", "Trip", "Station", "Latitude", "Longitude", "Datetime", "SerialNumber", "Sounder Depth", "Sample Size", "Comments", "Date", "Time", "Year", "Month", "Day"])
            writer.writerow(row)
            files.append(csvName)




if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
    select = input("Choose method for file selection\n[1] Read Files From: " + dirName + "\n[2] Manually Select Files")
    manualSelect = False

    def confirmSelection(select, dirName, manualSelect):
        if select == "1":
            files = dir_tk.getListOfFiles(dirName)
            return files
        if select == "2":
            files = dir_tk.selectFiles()
            manualSelect = True
            return files
        else:
            print("Invalid Input")
            select = input("Choose method for file selection\n[1] Read Files From: " + dirName + "\n[2] Manually Select Files\n")
            confirmSelection(select)

    files = confirmSelection(select, dirName, manualSelect)

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
                csvName = cast.ship.__str__() + cast.trip.__str__() + "_META.csv"
                writeMetaToCNV(cast,df)
            except Exception as e:
                x = input("ERROR: " + e.__str__() + "\nProgram Halted!\nPress Enter To Continue...")



