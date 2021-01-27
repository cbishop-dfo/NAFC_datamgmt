exec(open("C:\QA_paths\set_QA_paths.py").read())

from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import csv
from tkinter.filedialog import askopenfile
import pandas as pd
import sqlite3
from sqlalchemy import create_engine


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    print("Select Master File")
    file1 = askopenfile().name
    print("Select Joiner File")
    file2 = askopenfile().name

    Master = pd.read_excel(file1, header=1)
    Joiner = pd.read_excel(file2)
    Master["Date"] = Master["Date"].values.astype(str)
    Joiner["Date"] = Joiner["Date"].values.astype(str)
    Master["GMT"] = Master["GMT"].values.astype(str)
    Joiner["TimeUTC"] = Joiner["TimeUTC"].values.astype(str)

    masterDate = []
    joinerDate = []

    for d in Master["Date"].values:
        dat = d.split("T")[0]
        masterDate.append(dat)
    Master["Date"] = masterDate

    for d in Joiner["Date"].values:
        dat = d.split()[0]
        joinerDate.append(dat)
    Joiner["Date"] = joinerDate

    newdf = pd.merge(Joiner, Master, how="left", right_on=["Latitude", "Longitude", "Date", "GMT", "Section", "Station"], left_on=["Lat", "Lon", "Date", "TimeUTC", "Section", "Station"])
    newdf["SampleID"] = newdf["ID"]
    newdf = newdf[newdf['ShipTrip'].notna()]
    for n in range(24):
        i = len(newdf.columns)-1
        newdf = newdf.drop(newdf.columns[i], axis=1)
    newdf = newdf.drop_duplicates()
    newdf = newdf.drop_duplicates(subset=['SampleID'])
    filename = input("Enter name for file: ")
    newdf.to_excel(filename, index=False)

    print()

