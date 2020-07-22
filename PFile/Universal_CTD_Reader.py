import os
import tkinter as tk
from tkinter import filedialog
import sqlite3
import re
import numpy as np
import pandas as pd
import datetime
import xlrd


__author__ = 'KennedyDyl'
"""
Reader for P Files and SBE Files.
Script takes the file and converts it into a Cast object and is then stored in the database.
User will be prompted to change database path upon execution, Default is "CTD.db".
Script will try and read all supported formats .p and .sbe and write them to the database

-reader for the P files, writes to CTD.db, in "Data" Table
-reader for SBE files, writes to CTD.db, in "SBE_Data" Table

Reader pulls column names from the database when creating the dataframe. So if new columns need to be read, create a new 
field in the coresponding data table.
for SBE files: "SBE_Data" table in database
for P files: "Data" table in database
"""


class Cast(object):

    def __init__(self, datafile=None):
        self.datafile = datafile
        self.initialize_vars()

    def initialize_vars(self):

        # Meta Data
        self.id = ""
        self.ship = ""
        self.trip = ""
        self.station = ""
        self.ShipName = ""
        self.Latitude = ""
        self.Longitude = ""
        self.CastDatetime = ""
        self.SounderDepth = ""
        self.Instrument = ""
        self.InstrumentName = ""
        self.setNumber = ""
        self.castType = ""
        self.comment = ""
        self.NumScans = ""
        self.SamplingRate = ""
        self.filetype = ""
        self.channelCount = ""
        self.dataChannels = ""
        self.downcast = ""
        self.subsample = ""
        self.minDepth = ""
        self. maxDepth = ""
        self.fishingStrata = ""
        self.metData = ""
        self.DataLimit = ""

        self.columns = ""
        self.language = "English (Default)"
        self.encoding = "UTF-8 (Default)"

        # Data Identification
        self.PointOfContact = "Charlie Bishop, Email: Charlie.Bishop@dfo-mpo.gc.ca"
        self.OrgName = "NAFC"
        self.Country = "Canada"

        # Instrument Maintenance
        self.MaintenanceContact = "Steve Snook, Email: Stephen.Snook@dfo-mpo.gc.ca"
        self.CalibrationCoefficients = ""

        # Meteor Data
        self.Cloud = ""
        self.WinDir = ""
        self.WinSPD = ""
        self.wwCode = ""
        self.BarPres = ""
        self.TempWet = ""
        self.TempDry = ""
        self.WavPeroid = ""
        self.WavHeight = ""
        self.SwellDir = ""
        self.SwellPeroid = ""
        self.SwellHeight = ""
        self.IceConc = ""
        self.IceStage = ""
        self.IceBergs = ""

        # Data arrays and Database file
        self.data = []
        self.ColumnNames = []
        self.history = []
        self.channel = []
        self.header = []
        self.software = []
        self.userInput = []
        self.InstrumentInfo = []
        self.directory = 'CTD.db'  # DB Location.
        self.datafile = datafile

###########################################################################################################


def getShipName(cast):

    Ships = open("ships.txt")

    for shipName in Ships:
        number = shipName.replace("\n", "").split()[0]
        try:
            name = shipName.replace("\n", "").split()[1]
        except:
            continue
        if number == cast.ship:
            cast.ShipName = name
            break

###########################################################################################################

# Use for SBE or RSBE in future if met data is decided to be added to other files besides the p files
def read_met_file():
    try:
        # NOTE: Script requires _met.xlsx files in same directory as running script
        loc = dir_path + "\\" + cast.ship.__str__() + cast.trip.__str__() + "_met.xlsx"
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        # Loop through sheet rows.
        for i in range(sheet.nrows):
            if not sheet.cell_value(i, 0) == "cid":
                id = sheet.cell_value(i, 0)

                if int(id) == int(cast.id):
                    cast.Cloud = sheet.cell_value(i, 8)
                    cast.WinDir = sheet.cell_value(i, 9)
                    cast.WinSPD = sheet.cell_value(i, 10)
                    cast.wwCode = sheet.cell_value(i, 11)
                    cast.BarPres = sheet.cell_value(i, 12)
                    cast.TempWet = sheet.cell_value(i, 13)
                    cast.TempDry = sheet.cell_value(i, 14)
                    cast.WavPeroid = sheet.cell_value(i, 15)
                    cast.WavHeight = sheet.cell_value(i, 16)
                    cast.SwellDir = sheet.cell_value(i, 17)
                    cast.SwellPeroid = sheet.cell_value(i, 18)
                    cast.SwellHeight = sheet.cell_value(i, 19)
                    cast.IceConc = sheet.cell_value(i, 20)
                    cast.IceStage = sheet.cell_value(i, 21)
                    cast.IceBergs = sheet.cell_value(i, 22)
                    break
    except:
        pass

###########################################################################################################

def isMeta(data):
    meta = Cast()
    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    metadata = conn.cursor()
    metadata.execute("SELECT * FROM Casts")
    rows = metadata.fetchall()
    metareturn = False

    for row in rows:
        meta.id = row[0]
        meta.ship = row[1]
        meta.trip = row[2]
        meta.station = row[3]


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

def getInstrumentName(cast, refFile):

    dfs = pd.read_excel(refFile, sheet_name="Sheet1")
    #dfs = pd.read_csv(refFile, sep=" ", header=None)


    for i in dfs.index:
        if cast.Instrument.__contains__(dfs['Serial Number (SN)'][i].__str__()):
            cast.InstrumentName = dfs['Instrument Type (SBE-CTD)'][i]

###########################################################################################################

def convertDate(date):

    dateN = ""
    if date[0].upper().__contains__('JAN'):
        dateN = date[2] + '-01-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('FEB'):
        dateN = date[2] + '-02-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('MAR'):
        dateN = date[2] + '-03-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('APR'):
        dateN = date[2] + '-04-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('MAY'):
        dateN = date[2] + '-05-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('JUN'):
        dateN = date[2] + '-06-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('JUL'):
        dateN = date[2] + '-07-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('AUG'):
        dateN = date[2] + '-08-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('SEP'):
        dateN = date[2] + '-09-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('OCT'):
        dateN = date[2] + '-10-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('NOV'):
        dateN = date[2] + '-11-' + date[1] + " " + date[3]

    elif date[0].upper().__contains__('DEC'):
        dateN = date[2] + '-12-' + date[1] + " " + date[3]

    cast.CastDatetime = dateN




###########################################################################################################

def getMetData(cast):

    cast.Cloud = cast.metData[0:1]
    cast.WinDir = cast.metData[2:4]
    cast.WinSPD = cast.metData[5:7]
    cast.wwCode = cast.metData[8:10]
    cast.BarPres = cast.metData[11:17]
    cast.TempWet = cast.metData[18:23]
    cast.TempDry = cast.metData[24:29]
    cast.WavPeroid = cast.metData[30:32]
    cast.WavHeight = cast.metData[33:35]
    cast.SwellDir = cast.metData[36:38]
    cast.SwellPeroid = cast.metData[39:41]
    cast.SwellHeight = cast.metData[42:44]
    cast.IceConc = cast.metData[45:46]
    cast.IceStage = cast.metData[47:48]
    cast.IceBergs = cast.metData[49:50]

###########################################################################################################


def getChannelInfo(datafile):

    channelComplete = False
    isChannel = False

    with open(datafile, 'r') as f:
        for line in f:
            x = line.replace(" ", "*").split("*")
            if line.__contains__("-- CHANNEL STATS --"):
                isChannel = True
            if line.__contains__("-- END --"):
                isChannel = False
                channelComplete = True
            if isChannel:
                cast.channel.append(line.replace("\n", ""))

"""
    latitudes.units = 'degree_north'
    longitudes.units = 'degree_east'
    times.units = 'hours since 1900-01-01 00:00:00'
    times.calendar = 'gregorian'
    levels.units = 'dbar'
    levels.standard_name = "pressure"
    #levels.valid_range = np.array((0.0, 5000.0))
    levels.valid_min = 0
    temp.units = 'Celsius'
    temp.long_name = "Water Temperature" # (may be use to label plots)
    temp.standard_name = "sea_water_temperature"
    sal.long_name = "Practical Salinity"
    sal.standard_name = "sea_water_salinity"
    sal.units = "1"
    sal.valid_min = 0
    sigt.standard_name = "sigma_t"
    sigt.long_name = "Sigma-t"
    sigt.units = "Kg m-3"
    o2.long_name = "Dissolved Oxygen Concentration" ;
    o2.standard_name = "oxygen_concentration" ;
    o2.units = "ml L-1" ;
    cond.long_name = "Water Conductivity" ;
    cond.standard_name = "sea_water_conductivity" ;
    cond.units = "S m-1" ;
    fluo.long_name = "Chl-a Fluorescence" ;
    fluo.standard_name = "concentration_of_chlorophyll_in_sea_water" ;
    fluo.units = "mg m-3" ;
    par.long_name = "Irradiance" ;
    par.standard_name = "irradiance" ;
    par.units = "umol photons m-2 s-1" ;
    ph.long_name = "water PH" ;
    ph.standard_name = "PH" ;
    ph.units = "unitless" ;
"""

###########################################################################################################


def read_pFile(datafile):
    print("Reading: " + datafile)



    bohist_ = '-- HISTORY -->'
    eohist_ = '-- END --'
    in_history = False

    # Read history from header

    with open(datafile, 'r') as td:
        for line in td:
            # print (line) # for testing
            if line.startswith(bohist_) or line.startswith(">READ #"):  # begin-of-header
                cast.history.append(line)
                in_history = True
                continue
            if in_history:
                cast.history.append(line)
            if line.startswith(eohist_):  # end-of-header
                in_history = False

###########################################################################################################


def pfile_to_dataframe(filename):
    """Reads a pfile given in 'filename' as returns a Pandas.DataFrame with
       columns being the variables
    """
    eoh = '-- DATA --'
    in_header = True

    # Read header
    with open(filename, 'r') as td:
        for line in td:

            if re.match(eoh, line):  # end-of-header
                in_header = False
                continue  # ignore line
            elif in_header:  # read header
                cast.header.append(line)
            else:  # read data
                line = re.sub('\n', '', line)
                line = line.strip()
                line = re.sub(' +', ' ', line)
                cast.data.append(line.split(' '))

    # Read columns & remove last line of header
    cast.columns = cast.header[-1]
    cast.header = cast.header[:-1]

    d = cast.data[0]

    # clean columns
    cast.columns = re.sub('\n', '', cast.columns)
    cast.columns = cast.columns.strip()
    cast.columns = re.sub(' +', ' ', cast.columns)

    df = pd.DataFrame()


    """
    # List of all know columns
    # TODO: Get columns from the database, so if new columns are added to the database we can read in files with more cols
    allColumns = ["scan", "pres", "depth", "temp", "cond", "sal", "sigt", "oxy", "flor", "par", "pH", "trp", "tra", "wet"]
    """
    # List of columns pulled from database
    sqlite_file = cast.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("select * from Data")
    names = list(map(lambda x: x[0], c.description))
    names.remove("did")
    names.remove("cid")
    allColumns = names
    cast.ColumnNames = names

    Dictionary = {}
    for c in allColumns:
        Dictionary[c] = []

    for dat in cast.data:
        try:
            for i in allColumns:
                index = 0
                for j in cast.columns.split():
                    if i == j:
                        Dictionary[i].append(dat[index])
                        break
                    else:
                        index = index + 1
        except Exception as e:
            print(e)
            continue

    for column in Dictionary:
        try:
            df[column] = Dictionary[column]
        except:
            df[column] = np.nan
    return df

###########################################################################################################


def pfile_database(cast, df):

    sqlite_file = cast.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    def df2sqlite(dataframe, db_name="CTD.db", tbl_name="Data"):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        wildcards = ','.join(['?'] * (len(dataframe.columns) + 2)) # + 2 for did, cid
        # data = [tuple(x) for x in dataframe.values]
        data = []

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
                  " 'FishSet', 'CastType', 'Comment', 'NumScans', 'SamplingRate', 'FileType', 'ChannelCount', 'DataChannels',"
                  " 'Downcast', 'Subsample', 'MinDepth', 'MaxDepth', 'FishingStrata', 'Met', 'CastDatetime', 'File', 'Language', 'Encoding', 'Contact', 'Country', 'MaintenanceContact', 'OrgName', 'DataLimit' )"
                  " VALUES ( '{ID}', '{ship}', '{shipName}', '{trip}', '{sett}', '{lat}', '{long}', '{depth}', '{ins}', '{insname}', "
                  " '{fishset}', '{casttype}', '{comment}', '{numscan}', '{sample}', '{filetype}', '{chnlcount}', '{datchannels}', '{dcast}',"
                  " '{sub}', '{mind}', '{maxd}', '{fstrata}', '{meta}', '{date}', '{fil}', '{lang}', '{enc}', '{cnt}', '{coun}', '{mcnt}', '{onam}', '{dlmt}')" \
                  .format(ID=cast.id, ship=cast.ship, shipName=cast.ShipName, trip=cast.trip, sett=cast.station, lat=cast.Latitude, long=cast.Longitude,
                          depth=cast.SounderDepth, ins=cast.Instrument, fishset=cast.setNumber, casttype=cast.castType,
                          comment=cast.comment, numscan=cast.NumScans, sample=cast.SamplingRate, insname=cast.InstrumentName,
                          filetype=cast.filetype, chnlcount=cast.channelCount, datchannels=cast.dataChannels,
                          dcast=cast.downcast, sub=cast.subsample, mind=cast.minDepth, maxd=cast.maxDepth,
                          fstrata=cast.fishingStrata, meta=cast.metData, date=cast.CastDatetime, fil=datafile,
                          lang=cast.language, enc=cast.encoding, cnt=cast.PointOfContact, coun=cast.Country,
                          mcnt=cast.MaintenanceContact, onam=cast.OrgName, dlmt=cast.DataLimit))

        # Meteor Table
        c.execute(
            "INSERT INTO 'Meteor' ('MKey', 'cid', 'Cloud','WinDir','WinSPD','wwCode','BarPres','TempWet','TempDry','WavPeroid','WavHeight','SwellDir','SwellPeroid','SwellHeight','IceConc','IceStage','IceBerg')"
            " VALUES ( NULL, '{castID}', '{c}', '{wd}', '{ws}', '{ww}', '{bp}', '{tw}', '{td}', '{wp}', '{wh}', '{sd}', '{sp}', '{sh}', '{ic}', '{ist}', '{ib}')" \
                .format(castID=cast.id, c=cast.Cloud, wd=cast.WinDir, ws=cast.WinSPD, ww=cast.wwCode, bp=cast.BarPres,
                        tw=cast.TempWet, td=cast.TempDry, wp=cast.WavPeroid, wh=cast.WavHeight, sd=cast.SwellDir,
                        sp=cast.SwellPeroid, sh=cast.SwellHeight, ic=cast.IceConc, ist=cast.IceStage, ib=cast.IceBergs))

        # Header Table
        for l in cast.header:
            c.execute(
                "INSERT INTO 'Header' ('HKey', 'cid', 'Line')"
                " VALUES ( NULL, '{castID}', '{lin}')" \
                .format(castID=cast.id, lin=l.replace("'", "")))

        conn.commit()
        df2sqlite(df)

###########################################################################################################

def database(cast, df):

    sqlite_file = cast.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    def df2sqlite(dataframe, db_name="CTD.db", tbl_name="SBE_Data"):
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
                    cur.execute("ALTER TABLE SBE_Data ADD '{dfc}' Text".format(dfc=newcol))

            print("Adjusting Table Columns")

        conn.commit()
        conn.close()

        # isMeta Checks if identical data exists in database.

    # Casts Table
    if not isMeta(cast):
        c.execute("INSERT INTO 'Casts' ('id', 'Ship', 'ShipName', 'Trip', 'Station', 'Latitude', 'Longitude', 'SounderDepth', 'Instrument', 'InstrumentName',"
                  " 'FishSet', 'CastType', 'Comment', 'NumScans', 'SamplingRate', 'FileType', 'ChannelCount', 'DataChannels',"
                  " 'Downcast', 'Subsample', 'MinDepth', 'MaxDepth', 'FishingStrata', 'Met', 'CastDatetime', 'File', 'Language', 'Encoding', 'Contact', 'Country', 'MaintenanceContact', 'OrgName', 'DataLimit' )"
                  " VALUES ( '{ID}', '{ship}', '{shipName}', '{trip}', '{sett}', '{lat}', '{long}', '{depth}', '{ins}', '{insname}', "
                  " '{fishset}', '{casttype}', '{comment}', '{numscan}', '{sample}', '{filetype}', '{chnlcount}', '{datchannels}', '{dcast}',"
                  " '{sub}', '{mind}', '{maxd}', '{fstrata}', '{meta}', '{date}', '{fil}', '{lang}', '{enc}', '{cnt}', '{coun}', '{mcnt}', '{onam}', '{dlmt}')" \
                  .format(ID=cast.id, ship=cast.ship, shipName=cast.ShipName, trip=cast.trip, sett=cast.station, lat=cast.Latitude, long=cast.Longitude,
                          depth=cast.SounderDepth, ins=cast.Instrument, fishset=cast.setNumber, casttype=cast.castType,
                          comment=cast.comment, numscan=cast.NumScans, sample=cast.SamplingRate, insname=cast.InstrumentName,
                          filetype=cast.filetype, chnlcount=cast.channelCount, datchannels=cast.dataChannels,
                          dcast=cast.downcast, sub=cast.subsample, mind=cast.minDepth, maxd=cast.maxDepth,
                          fstrata=cast.fishingStrata, meta=cast.metData, date=cast.CastDatetime, fil=datafile,
                          lang=cast.language, enc=cast.encoding, cnt=cast.PointOfContact, coun=cast.Country,
                          mcnt=cast.MaintenanceContact, onam=cast.OrgName, dlmt=cast.DataLimit))

        # Meteor Table
        c.execute(
            "INSERT INTO 'Meteor' ('MKey', 'cid', 'Cloud','WinDir','WinSPD','wwCode','BarPres','TempWet','TempDry','WavPeroid','WavHeight','SwellDir','SwellPeroid','SwellHeight','IceConc','IceStage','IceBerg')"
            " VALUES ( NULL, '{castID}', '{c}', '{wd}', '{ws}', '{ww}', '{bp}', '{tw}', '{td}', '{wp}', '{wh}', '{sd}', '{sp}', '{sh}', '{ic}', '{ist}', '{ib}')" \
                .format(castID=cast.id, c=cast.Cloud, wd=cast.WinDir, ws=cast.WinSPD, ww=cast.wwCode, bp=cast.BarPres,
                        tw=cast.TempWet, td=cast.TempDry, wp=cast.WavPeroid, wh=cast.WavHeight, sd=cast.SwellDir,
                        sp=cast.SwellPeroid, sh=cast.SwellHeight, ic=cast.IceConc, ist=cast.IceStage, ib=cast.IceBergs))

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
        df2sqlite(df)

###########################################################################################################

def sbe_to_dataframe(filename,cast):
    """Reads a pfile given in 'filename' as returns a Pandas.DataFrame with
       columns being the variables
    """

    # Read columns & remove last line of header
    cast.columns = cast.data.pop(0)
    cast.header = cast.header[:-1]

    df = pd.DataFrame()

    # List of all known columns
    """
    # TODO: Get columns from the database, so if new columns are added to the database we can read in files with more cols
    allColumns = ["Scan", "PrdM", "T090C", "T190C", "C0S_m", "C1S_m", "Sbeox0V", "Ph", "Ph2", "Sbeox1V", "Par",
                  "Par_log", "Par_sat_log", "flSP", "FlSPuv0", "Upoly0", "Sbeox0ML_L", "Sbeox1ML_L", "Sal00",
                  "Sal11", "Sigma_t00", "Sigma_t11", "OxsatML_L", "FlECO_AFL", "Tv290C", "WetCDOM",
                  "CStarAt0", "CStarTr0"]
    """
    # List of columns pulled from database.
    sqlite_file = cast.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute("select * from SBE_Data")
    names = list(map(lambda x: x[0], c.description))
    names.remove("sid")
    names.remove("cid")
    allColumns = names

    Dictionary = {}
    for c in allColumns:
        Dictionary[c] = []

    for dat in cast.data:
        try:
            for i in allColumns:
                index = 0
                for j in cast.columns:
                    if i == j.replace("-","_").replace("/", "_"):
                        Dictionary[i].append(dat[index])
                        break
                    else:
                        index = index + 1
        except Exception as e:
            print(e)
            continue

    for column in Dictionary:
        try:
            df[column] = Dictionary[column]
        except:
            df[column] = np.nan
    return df

###########################################################################################################

def sbe_meta(datafile):

    f = open(datafile)
    isData = False
    for line in f:
        line = line.replace("\n", "")

        if isData:
            cast.data.append(line.replace("\n", "").lstrip().rstrip().split())

        elif line.__contains__("** "):
            cast.userInput.append(line)
            if line.upper().__contains__("VESSEL"):
                cast.id = line.split(':')[1].lstrip().rstrip()
                cast.ship = cast.id[0:2]
                cast.trip = cast.id[2:5]
                cast.station = cast.id[5:8]

            elif line.upper().__contains__("LATITUDE"):
                line = line.lower().replace("n", "")
                lat = line.split(":")[1].lstrip().rstrip()
                if lat.__len__() >= 5 and not lat.__contains__(" "):
                    x = lat[0:2]
                    y = lat[2:4] + "." + lat[4:]
                    lat = x + " " + y

                cast.Latitude = convertLatLong(lat.split())

            elif line.upper().__contains__("LONGITUDE"):
                isNeg = False

                if line.__contains__("-"):
                    isNeg = True

                line = line.lower().replace("w", "")
                lon = line.split(":")[1].lstrip().rstrip()
                if lon.__len__() >= 5 and not lon.__contains__(" "):
                    x = lon[0:2]
                    y = lon[2:4] + "." + lon[4:]
                    lon = x + " " + y

                if not isNeg:
                    lon = "-" + lon

                cast.Longitude = convertLatLong(lon.split())

            elif line.upper().__contains__("SOUNDING"):
                cast.SounderDepth = line.split(":")[1]
            elif line.upper().__contains__("COMMENTS"):
                cast.comment = line.split(":")[1]

            elif line.upper().__contains__("PROBE"):
                cast.Instrument = line.split(":")[1]

            elif line.upper().__contains__("YEAR"):
                year = line.split(":")[1].rstrip().lstrip()
            elif line.upper().__contains__("MONTH"):
                month = line.split(":")[1].rstrip().lstrip()
            elif line.upper().__contains__("DAY"):
                day = line.split(":")[1].rstrip().lstrip()
            elif line.upper().__contains__("HOURS/MIN"):
                time = line.split(":")[1].rstrip().lstrip()
                time = time[0:2] + ":" + time[2:4]
                casttime =  year + "-" + month + "-" + day + " " + time
                cast.CastDatetime = casttime
            elif line.upper().__contains__("FORMAT"):
                cast.castType = line.split(":")[1]

            elif line.upper().__contains__("METDATA"):
                cast.metData = line.split(":")[1].replace(" " + cast.id, "")[1:]
                getMetData(cast)

        elif line.startswith("* "):
            cast.software.append(line)


        elif line.startswith("# "):
            cast.InstrumentInfo.append(line)
            if line.lower().__contains__("start_time"):
                dateArray = []
                date = line.split("=")[1].split()


                convertDate(date)

        else:
            isData = True

    getShipName(cast)
    getInstrumentName(cast, "CTD Instrument Info.xlsx")

    # If Met File exists for SBE file types
    read_met_file()

###########################################################################################################


def pfile_meta(datafile):

    line = cast.header[1]
    nextLine = cast.header[2]
    lastLine = cast.header[3]
    cast.ship = line[0:2]
    cast.trip = line[2:5]
    cast.station = line[5:8]
    cast.id = int(cast.ship.__str__() + cast.trip.__str__() + cast.station.__str__())

    lat = line[9:17].split()
    long = line[18:30].split()
    cast.Latitude = convertLatLong(lat)
    cast.Longitude = convertLatLong(long)

    date = line[30:46]
    cast.CastDatetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')

    cast.SounderDepth = line[47:51]
    cast.Instrument = line[52:57]
    cast.setNumber = line[58:61]
    cast.castType = line[62:63]
    cast.comment = line.replace("\n", "")[63:-1].replace("'", "").rstrip()

    cast.NumScans = nextLine[9:15]
    cast.SamplingRate = nextLine[16:21]
    cast.filetype = nextLine[22:23]
    cast.channelCount = nextLine[24:26]
    cast.dataChannels = nextLine[28:47]
    temp = nextLine.replace("\n", "")[59:-2]
    cast.downcast = temp[0:1]
    cast.subsample = temp[2:5]
    cast.minDepth = temp[6:10]
    cast.maxDepth = temp[11:15]
    cast.fishingStrata = temp[16:20]

    # Meteor Data
    cast.metData = lastLine.rstrip()[9:-1]
    cast.Cloud = cast.metData[0:1]
    cast.WinDir = cast.metData[2:4]
    cast.WinSPD = cast.metData[5:7]
    cast.wwCode = cast.metData[8:10]
    cast.BarPres = cast.metData[11:17]
    cast.TempWet = cast.metData[18:23]
    cast.TempDry = cast.metData[24:29]
    cast.WavPeroid = cast.metData[30:32]
    cast.WavHeight = cast.metData[33:35]
    cast.SwellDir = cast.metData[36:38]
    cast.SwellPeroid = cast.metData[39:41]
    cast.SwellHeight = cast.metData[42:44]
    cast.IceConc = cast.metData[45:46]
    cast.IceStage = cast.metData[47:48]
    cast.IceBergs = cast.metData[49:50]

    getInstrumentName(cast, "CTD Instrument Info.xlsx")
    getShipName(cast)

###########################################################################################################

# Convert Lat / Long into decimals
def convertLatLong(convert):
    if convert.__len__() == 2:
        value = abs(float(convert[0])) + float(convert[1]) / 60
        value = float("{0:.2f}".format(value))
        if convert[0].__contains__("-"):
            return -value
        return value
    elif convert.__len__() == 3:
        x = float(convert[2]) / 60
        y = x + float(convert[1])
        z = y / 60
        value = float(convert[0].replace('-', "")) + z
        value = float("{0:.2f}".format(value))
        return value
    else:
        return convert[0]

###########################################################################################################


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # if entry.endswith('.rpf'):
        allFiles.append(entry)
    return allFiles

###########################################################################################################


# If no subfolder called Problem_Files exists, creates new sub folder BadSampleSize to write files to.
def createProblemFolder():
    current_path = os.path.dirname(os.path.realpath(__file__))

    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\Problem_Files\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)


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
        files = getListOfFiles(dirName)

    for f in files:

        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".sbe"):
            try:
                print("Reading: " + datafile)
                cast = Cast(datafile)
                sbe_meta(datafile)
                df = sbe_to_dataframe(datafile, cast)
                cast.DataLimit = len(df.index)
                database(cast, df)
            except Exception as e:
                os.chdir(dirName)
                createProblemFolder()
                newfile = datafile.replace(".sbe", "_") + ".error"
                print("Error Reading File")
                f = open(newfile, "w")
                f.write(e.__str__())

        elif datafile.lower().__contains__(".p") and not datafile.lower().__contains__(".py"):
            try:
                cast = Cast(datafile)
                read_pFile(datafile)
                getChannelInfo(datafile)
                df = pfile_to_dataframe(datafile)
                cast.DataLimit = len(df.index)
                pfile_meta(datafile)
                pfile_database(cast, df)
            except Exception as e:
                createProblemFolder()
                newfile = datafile.replace(".p", "_") + ".error"
                print("Error Reading File")
                f = open(newfile, "w")
                f.write(e.__str__())

        else:
            print("File Not Supported...")

    print("******************************")
    input("Press Enter To Finish")