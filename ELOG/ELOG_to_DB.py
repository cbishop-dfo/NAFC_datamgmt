exec(open("C:\QA_paths\set_QA_paths.py").read())


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



if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    directory = db_tk.setDirectory()
    files = dir_tk.confirmSelection(dirName)
    for f in files:
        # changes Dir back to original
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f

        if datafile.lower().endswith(".log"):
            f = open(datafile)
            Date = ""
            Replyto = ""
            Event = ""
            Station = ""
            Instrument = ""
            Attached = ""
            Action = ""
            Sounding = ""
            Sample_ID = ""
            End_Sample_ID = ""
            WireOut = ""
            Depth = ""
            Author = ""
            Seq_Number = ""
            IMEI_No = ""
            WMO_No = ""
            SN = ""
            Name = ""
            Comment = ""
            TimePosition = ""
            Cruise = ""
            PI = ""
            Protocol = ""
            Platform = ""
            Revisions = ""
            Attachment = ""
            Encoding = ""

            for line in f:
                line = line.replace("\n", "")
                if line.__contains__("Date"):
                    Date = line.split(": ")[1]
                    datetime = Date.split(" ")
                    day = datetime[1]
                    month = datetime[2]
                    year = datetime[3]
                    time = datetime[4]
                    timezone = datetime[5]
                elif line.__contains__("Reply to:"):
                    Replyto = line.split(":")[1]
                elif line.__contains__("Event:"):
                    Event = line.split(":")[1]
                elif line.__contains__("Station:"):
                    Station = line.split(":")[1]
                elif line.__contains__("Instrument:"):
                    Instrument = line.split(":")[1]
                elif line.__contains__("Attached:"):
                    Attached = line.split(":")[1]
                elif line.__contains__("Action:"):
                    Action = line.split(":")[1]
                elif line.__contains__("Sounding:"):
                    Sounding = line.split(":")[1]
                elif line.__contains__("End_Sample_ID:"):
                    End_Sample_ID = line.split(":")[1]
                elif line.__contains__("Sample_ID:"):
                    Sample_ID = line.split(":")[1]
                elif line.__contains__("Wire Out:"):
                    WireOut = line.split(":")[1]
                elif line.__contains__("Depth:"):
                    Depth = line.split(":")[1]
                elif line.__contains__("Author:"):
                    Author = line.split(":")[1]
                elif line.__contains__("Seq_Number:"):
                    Seq_Number = line.split(":")[1]
                elif line.__contains__("IMEI_No:"):
                    IMEI_No = line.split(":")[1]
                elif line.__contains__("WMO_No:"):
                    WMO_No = line.split(":")[1]
                elif line.__contains__("S/N:"):
                    SN = line.split(":")[1]
                elif line.__contains__("Name:"):
                    Name = line.split(":")[1]
                elif line.__contains__("Comment:"):
                    Comment = line.split(":")[1]
                elif line.__contains__("Time|Position:"):
                    TimePosition = line.split(":")[1]
                    tp = TimePosition.split("|")
                    isoTime = tp[0]
                    latitude = tp[2]
                    longitude = tp[3]
                    Lat = cnv_tk.convertLatLong([latitude.split()[0], latitude.split()[1]]).__str__() + " " + latitude.split()[2]
                    Lon = cnv_tk.convertLatLong([longitude.split()[0], longitude.split()[1]]).__str__() + " " + longitude.split()[2]
                elif line.__contains__("Cruise:"):
                    Cruise = line.split(":")[1]
                elif line.__contains__("PI:"):
                    PI = line.split(":")[1]
                elif line.__contains__("Protocol:"):
                    Protocol = line.split(":")[1]
                elif line.__contains__("Platform:"):
                    Platform = line.split(":")[1]
                elif line.__contains__("Revisions:"):
                    Revisions = line.split(":")[1]
                elif line.__contains__("Attachment:"):
                    Attachment = line.split(":")[1]
                elif line.__contains__("Encoding:"):
                    Encoding = line.split(":")[1]
                elif line.__contains__("==="):

                    sqlite_file = directory
                    conn = sqlite3.connect(sqlite_file)
                    c = conn.cursor()

                    Row = [Date, day, month, year, time, timezone, Replyto, Event, Station, Instrument, Attached,
                           Action, Sounding,
                           Sample_ID, End_Sample_ID, WireOut, Depth, Author, Seq_Number, IMEI_No, WMO_No,
                           SN, Name, Comment, isoTime, latitude, longitude, Lat, Lon, Cruise, PI, Protocol, Platform,
                           Revisions, Attachment, Encoding]

                    # ELOG Table
                    # Remove full path from file and only include filename in database
                    OGfile = datafile.split("/")
                    OGfile = OGfile[OGfile.__len__() - 1]
                    c.execute(
                        "INSERT INTO 'ELOG' ('id', 'Date', 'day', 'month', 'year', 'time', 'timezone', 'Replyto', 'Event', 'Station', 'Instrument', 'Attached', 'Action', 'Sounding',"
                        "'Sample_ID', 'End_Sample_ID', 'WireOut', 'Depth', 'Author', 'Seq_Number', 'IMEI_No', 'WMO_No',"
                        "'SN', 'Name', 'Comment', 'isoTime', 'latitude', 'longitude', 'Lat', 'Lon', 'Cruise', 'PI', 'Protocol', 'Platform',"
                        "'Revisions', 'Attachment', 'Encoding', 'File')"
                        " VALUES ( NULL, '{date}', '{day}', '{month}', '{year}', '{time}', '{timezone}', '{rpt}', '{evnt}', '{stn}', "
                        " '{ins}', '{att}', '{act}', '{sound}', '{sid}', '{esid}', '{wout}', '{depth}', '{aut}', '{segnum}', '{imei}', '{wmo}', '{sn}', '{name}', '{comm}', '{isot}',"
                        " '{lati}', '{longi}', '{lat}', '{lon}', '{cruise}', '{pi}', '{prot}', '{plat}', '{rev}', '{attach}', '{enc}', '{fle}')" \
                        .format(
                                date=Date.__str__(),
                                day=day.__str__(),
                                month=month.__str__(),
                                year=year.__str__(),
                                time=time.__str__(),
                                timezone=timezone.__str__(),
                                rpt=Replyto.__str__(),
                                evnt=Event.__str__(),
                                stn=Station.__str__(),
                                ins=Instrument.__str__(),
                                att=Attached.__str__(),
                                act=Action.__str__(),
                                sound=Sounding.__str__(),
                                sid=Sample_ID.__str__(),
                                esid=End_Sample_ID.__str__(),
                                wout=WireOut.__str__(),
                                depth=Depth.__str__(),
                                aut=Author.__str__(),
                                segnum=Seq_Number.__str__(),
                                imei=IMEI_No.__str__(),
                                wmo=WMO_No.__str__(),
                                sn=SN.__str__(),
                                name=Name.__str__(),
                                comm=Comment.__str__(),
                                isot=isoTime.__str__(),
                                lati=latitude.__str__(),
                                longi=longitude.__str__(),
                                lat=Lat.__str__(),
                                lon=Lon.__str__(),
                                cruise=Cruise.__str__(),
                                pi=PI.__str__(),
                                prot=Protocol.__str__(),
                                plat=Platform.__str__(),
                                rev=Revisions.__str__(),
                                attach=Attachment.__str__(),
                                enc=Encoding.__str__(),
                                fle=OGfile.__str__()))
                    conn.commit()
                    conn.close()



                    csvName = datafile + "_converted.csv"
                    Date = ""
                    Replyto = ""
                    Event = ""
                    Station = ""
                    Instrument = ""
                    Attached = ""
                    Action = ""
                    Sounding = ""
                    Sample_ID = ""
                    End_Sample_ID = ""
                    WireOut = ""
                    Depth = ""
                    Author = ""
                    Seq_Number = ""
                    IMEI_No = ""
                    WMO_No = ""
                    SN = ""
                    Name = ""
                    Comment = ""
                    TimePosition = ""
                    Cruise = ""
                    PI = ""
                    Protocol = ""
                    Platform = ""
                    Revisions = ""
                    Attachment = ""
                    Encoding = ""

                    datetime = ""
                    day = ""
                    month = ""
                    year = ""
                    time = ""
                    timezone = ""

                    tp = ""
                    isoTime = ""
                    latitude = ""
                    longitude = ""