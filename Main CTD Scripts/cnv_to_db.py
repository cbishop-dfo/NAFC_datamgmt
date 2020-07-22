import os
import tkinter as tk
from tkinter import filedialog
import sqlite3
import re
import numpy as np
import pandas as pd
import datetime
import xlrd
from Toolkits import cnv_tk
from Toolkits import dir_tk
from Toolkits import db_tk


__author__ = 'KennedyDyl'

###########################################################################################################

def isMeta(data):
    meta = cnv_tk.Cast(datafile)
    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    metadata = conn.cursor()
    metadata.execute("SELECT * FROM Casts")
    rows = metadata.fetchall()
    metareturn = False

    for row in rows:
        meta.id = row[0]
        meta.ship = row[2]
        meta.trip = row[3]
        meta.station = row[4]


        # Check Ship, Trip, Station for match
        fields = ["ship", "trip", "station"]

        # counter for number of matches of same fields
        sameFields = 0


        for field in fields:
            if getattr(meta, field) == getattr(data, field):
                sameFields = sameFields + 1


            # At least one field is different, no need so compare the others
            else:
                break

            if sameFields == fields.__len__():
                # Same Ship, Trip, Station exists in the database
                metareturn = True
                return metareturn

    return metareturn



###########################################################################################################

def database(cast, df):

    sqlite_file = cast.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    def df2sqlite(dataframe, db_name="CNV.db", tbl_name="Data"):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        wildcards = ','.join(['?'] * (len(dataframe.columns) + 2)) # + 2 for did cid
        # data = [tuple(x) for x in dataframe.values]
        data = []
        # Formatting data for Data table in Database, cid is cast id and did set to None so it auto increments
        for x in dataframe.values:
            cid = cast.id.__str__()
            did = None
            temp = []

            temp.append(did)
            temp.append(cid)
            for d in x:
                temp.append(d)
            data.append(temp)

        try:
            cur.executemany("insert into %s values(%s)" % (tbl_name, wildcards), data)
        except Exception as e:

            print(e)
            print(dataframe.columns)

            for dc in dataframe.columns:
                if dc not in cast.ColumnNames:
                    newcol = dc
                    cur.execute("ALTER TABLE Data ADD '{dfc}' Text".format(dfc=newcol))

            print("Adjusting Table Columns")

        conn.commit()
        conn.close()

        # isMeta Checks if identical data exists in database.

    # Casts Table
    if not isMeta(cast):
        c.execute("INSERT INTO 'Casts' ('id', 'Ship', 'ShipName', 'Trip', 'Station', 'Latitude', 'Longitude', 'SounderDepth', 'Instrument', 'InstrumentName',"
                  " 'Comment', 'NumScans', 'SamplingRate', 'ChannelCount', 'DataChannels',"
                  " 'MinDepth', 'MaxDepth', 'CastDatetime', 'File', 'Language', 'Encoding', 'Contact', 'Country', 'MaintenanceContact', 'OrgName', 'DataLimit' )"
                  " VALUES ( '{ID}', '{ship}', '{shipName}', '{trip}', '{sett}', '{lat}', '{long}', '{depth}', '{ins}', '{insname}', "
                  " '{comment}', '{numscan}', '{sample}', '{chnlcount}', '{datchannels}',"
                  " '{mind}', '{maxd}', '{date}', '{fil}', '{lang}', '{enc}', '{cnt}', '{coun}', '{mcnt}', '{onam}', '{dlmt}')" \
                  .format(ID=cast.id, ship=cast.ship, shipName=cast.ShipName, trip=cast.trip, sett=cast.station, lat=cast.Latitude, long=cast.Longitude,
                          depth=cast.SounderDepth, ins=cast.Instrument, fishset=cast.setNumber, casttype=cast.castType,
                          comment=cast.comment, numscan=cast.NumScans, sample=cast.SamplingRate, insname=cast.InstrumentName,
                          filetype=cast.filetype, chnlcount=cast.channelCount, datchannels=cast.dataChannels,
                          dcast=cast.downcast, sub=cast.subsample, mind=cast.minDepth, maxd=cast.maxDepth,
                          fstrata=cast.fishingStrata, meta=cast.metData, date=cast.CastDatetime, fil=datafile,
                          lang=cast.language, enc=cast.encoding, cnt=cast.PointOfContact, coun=cast.Country,
                          mcnt=cast.MaintenanceContact, onam=cast.OrgName, dlmt=cast.DataLimit))

        # User Input Table
        for l in cast.userInput:
            c.execute(
                "INSERT INTO 'Header' ('HKey', 'cid', 'Line')"
                " VALUES ( NULL, '{castID}', '{lin}')" \
                .format(castID=cast.id, lin=l.replace("'", "")))

        # Software
        for l in cast.software:
            c.execute(
                "INSERT INTO 'Software' ('sKey', 'cid', 'Software_Info')"
                " VALUES ( NULL, '{castID}', '{lin}')" \
                    .format(castID=cast.id, lin=l.replace("'", "")))
        # Instrument Info Table
        for l in cast.InstrumentInfo:
            c.execute(
                "INSERT INTO 'Instrument' ('iKey', 'cid', 'Instrument_Info')"
                " VALUES ( NULL, '{castID}', '{lin}')" \
                    .format(castID=cast.id, lin=l.replace("'", "")))

        conn.commit()
        #TODO: implement df into db for cnv
        # df2sqlite(df)

###########################################################################################################


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path



    print("Files to Process\n[1] All Files In Current Directory\n[2] Manual File Select")
    select = input()

    if select.__eq__("2"):
        root = tk.Tk()
        root.withdraw()
        files = filedialog.askopenfilenames(title='Choose files')
        print(files)

    if select.__eq__("1"):
        files = dir_tk.getListOfFiles(dirName)

    for f in files:

        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            try:
                print("Reading: " + datafile)
                cast = cnv_tk.Cast(datafile)
                cnv_tk.cnv_meta(cast, datafile)
                df = cnv_tk.cnv_to_dataframe(cast)
                cast.DataLimit = len(df.index)

                # TODO: Take user input as option
                cast.directory = 'CNV.db'

                database(cast, df)
            except Exception as e:
                os.chdir(dirName)
                dir_tk.createProblemFolder()
                newfile = datafile.replace(".cnv", "_") + "_cnv.error"
                print("Error Reading File")
                f = open(newfile, "w")
                f.write(e.__str__())


        else:
            print("File Not Supported...")

    print("******************************")
    input("Press Enter To Finish")