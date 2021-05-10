from Toolkits import dir_tk
from Toolkits import cnv_tk
from Toolkits import ships_biological
import os
import csv
import pandas as pd
def writeRow(csvName, row):


    fileExists = False
    for f in files:
        if f == csvName:
            fileExists = True

    if fileExists:
        with open(csvName, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(row)

    elif not fileExists:
        with open(csvName, 'w+', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Date", "day", "month", "year", "time", "timezone", "Replyto", "Event", "Station", "Instrument", "Attached", "Action", "Sounding",
                            "Sample_ID", "End_Sample_ID", "WireOut", "Depth", "Author", "Seq_Number", "IMEI_No", "WMO_No",
                            "SN", "Name", "Comment", "isoTime", "latitude", "longitude", "Latitude(Converted)", "Longitude(Converted)", "Cruise", "PI", "Protocol", "Platform",
                            "Revisions", "Attachment", "Encoding"])
            writer.writerow(row)
            files.append(csvName)

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

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
                    Row = [Date, day, month, year, time, timezone, Replyto, Event, Station, Instrument, Attached, Action, Sounding,
                            Sample_ID, End_Sample_ID, WireOut, Depth, Author, Seq_Number, IMEI_No, WMO_No,
                            SN, Name, Comment, isoTime, latitude, longitude, Lat, Lon, Cruise, PI, Protocol, Platform,
                            Revisions, Attachment, Encoding]
                    csvName = datafile + "_converted.csv"
                    writeRow(csvName, Row)
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