import Tkinter as tk
from Tkinter import *
import numpy as np
import pandas as pd
import os
import sqlite3
from sqlite3 import Error
from mpl_toolkits.basemap import Basemap
import matplotlib
import datetime
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
import math
# Only needed if code is changed to write out NETCDF's
import xlrd
import time as tt
try:
    import netCDF4 as nc
except:
    pass

"""
Script takes all casts from the CTD.db and plots them on a Basemap based on their Latitude and Longitude, and writes 
selected casts to a folder in choosn format.
created by Dylan Kennedy, 2019-08-20

**Script Running on Anaconda2, some modules may need to be downgraded due to basemap. See "Python Version Info.xlsx"
in "O:\Shared\Oceanography - Biological & Physical\Bishop\DataArchive\PhysicalData\Dylan" for more details.

*******************************************************************************************************************
User can select casts by:
1) Ship
2) Ship and Trip
3) Ship, Trip, Station
4) Year
5) Month
6) Year and Month
7) Area Between Specified Min/Max Latitudes and Longitudes

All selected id's to be written out are printed to the information textbox to the right of the map, user can scroll
to view the id's and copy them if needed.

Multiple selects can be done to query multiple casts.
Once casts are selected user can choose an output format to write out to.
supported outputs include:
1) NETCDF Files
2) RSBE Files
3) SBE Files
4) P Files

A reset button is included to clear all selections and redraw casts on the map.
The matplotlib toolbar is included with the map, user can zoom, pan, save, ect.
*******************************************************************************************************************
"""

###########################################################################################################


class Cast(object):

    def __init__(self):
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
        self.maxDepth = ""
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
        self.history = []
        self.channel = []
        self.header = []
        self.directory = 'CTD.db'  # DB Location.


###########################################################################################################

class Map():
    def __init__(self, database="CTD.db"):
        self.database = database
        self.initialize_vars()

    def initialize_vars(self):
        print("Initializing...")
        self.lats_all = []
        self.lons_all = []
        self.lats_used = []
        self.lons_used = []
        self.selectedIDs = []
        self.output = []

    def getPoints(self):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()
            c.execute("SELECT id, Latitude, Longitude FROM Casts")
            meta = c.fetchall()
            for m in meta:
                self.lats_all.append(float(m[1]))
                self.lons_all.append(float(m[2]))

            minlats = min(self.lats_all)
            maxlats = max(self.lats_all)
            minlons = min(self.lons_all)
            maxlons = max(self.lons_all)

            try:
                self.map = Basemap(projection='merc', lat_0=57, lon_0=-135, lat_ts=57, resolution=None, area_thresh=0.1,
                                   llcrnrlon=minlons - 12, llcrnrlat=minlats - 6.0, urcrnrlon=maxlons + 8.0,
                                   urcrnrlat=maxlats + 10.0)
            except Exception as e:
                print e
                self.map = Basemap(width=12000000, height=9000000, projection='lcc', resolution=None, lat_1=45.,
                                   lat_2=55,
                                   lat_0=50, lon_0=-107.)

            self.map.bluemarble()
            self.map.drawparallels(np.arange(10, 70, 2), linewidth=0)  # [left,right,top,bottom]
            self.map.drawmeridians(np.arange(-100, 0, 4), linewidth=0)

            x_all, y_all = self.map(np.array(self.lons_all), np.array(self.lats_all))
            self.map.scatter(x_all, y_all, 60, marker='o', color='b', edgecolors='k')

        except Error as err:
            print(err)


###########################################################################################################


def createFolder(foldername):
    current_path = os.path.dirname(os.path.realpath(__file__))

    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\" + foldername + "\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)


###########################################################################################################


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        print(err)

###########################################################################################################

def resetMap():
    map.selectedIDs = []
    map.lats_used = []
    map.lons_used = []
    map.getPoints()
    canvas.draw_idle()
    textBox.delete(1.0, END)
    textBox.insert(INSERT, "Files: " + "0" + "\n")

###########################################################################################################

def retrieve_input(map):

    # Get Entry Values
    ShipBoxValue = ShipBox.get()
    TripBoxValue = TripBox.get()
    StationBoxValue = StationBox.get()
    YearBoxValue = YearBox.get()
    MonthBoxValue = MonthBox.get()
    LatMaxBoxValue = LatMaxBox.get()
    LongMaxBoxValue = LongMaxBox.get()
    LatMinBoxValue = LatMinBox.get()
    LongMinBoxValue = LongMinBox.get()


    # Add lat/lons to be plotted on the map and save id's for writing.
    def addLocation(m):
        map.lats_used.append(float(m[1]))
        map.lons_used.append(float(m[2]))
        map.selectedIDs.append(int(m[0]))

    conn = create_connection(database)
    c = conn.cursor()
    c.execute("SELECT id, Latitude, Longitude, CastDatetime, Ship, Trip, Station FROM Casts")
    meta = c.fetchall()
    for m in meta:
        # Lats/Lons
        if not LatMaxBoxValue == '':
            if float(m[1]) <= float(LatMaxBoxValue) and float(m[1]) >= float(LatMinBoxValue) and float(m[2]) <= float(
                    LongMaxBoxValue) and float(m[2]) >= float(LongMinBoxValue):
                addLocation(m)
        # Ship Trip Station
        if not ShipBoxValue == '' and not TripBoxValue == '':
            # Gets all id's that match Ship and Trip.
            if StationBoxValue == '':
                if int(m[4]) == int(ShipBoxValue) and int(m[5]) == int(TripBoxValue):
                    addLocation(m)
            # Will get one id based on Ship, Trip and Station.
            elif not StationBoxValue == '':
                if int(m[4]) == int(ShipBoxValue) and int(m[5]) == int(TripBoxValue) and int(m[6]) == int(
                        StationBoxValue):
                    addLocation(m)
        # Ship only
        elif not ShipBoxValue == '':
            if int(m[4]) == int(ShipBoxValue):
                addLocation(m)

        elif LatMaxBoxValue == '':
            if not YearBoxValue == '':
                # Year Only
                if MonthBoxValue == '':
                    dbYear = m[3].lstrip()[0:4].__str__()
                    if dbYear == YearBoxValue:
                        addLocation(m)

                # Year and Month
                if not MonthBoxValue == '':
                    dbYear = m[3].lstrip()[0:4].__str__()
                    dbMonth = m[3].lstrip()[5:7].__str__()
                    if dbYear == YearBoxValue and dbMonth == MonthBoxValue:
                        addLocation(m)
            # Month Only
            elif not MonthBoxValue == '':
                dbMonth = m[3].lstrip()[5:7].__str__()
                if dbMonth == MonthBoxValue:
                    addLocation(m)

    # Convert the lat and lon to projection co-ordinates and plot
    print("Plotting")

    print(map.lats_used)
    x_used, y_used = map.map(np.array(map.lons_used), np.array(map.lats_used))
    map.map.scatter(x_used, y_used, 60, marker='o', color='r', edgecolors='k')
    plt.title("CTD Casts", fontsize=16)
    plt.legend(numpoints=1)
    canvas.draw_idle()
    print("Finished Drawing")

    textBox.delete(1.0, END)
    textBox.insert(INSERT, "Files: " + map.selectedIDs.__len__().__str__() + "\n")
    for t in map.selectedIDs:
        t = t.__str__() + "\n"
        textBox.insert(INSERT, t)


###########################################################################################################


# TODO: Finish depth calculation if needed
def calculateDepth(cast, pressure):
    lat = cast.Latitude
    p = pressure
    x = pow(math.sin(float(lat / 57.29578)), 2)
    g1 = 1.0 + ((5.2788 * pow(10, -3) + 2.36 * pow(10, -5 * x)) * x)
    g = 9.780318 * g1 + 1.092 * pow(10, -6) * p

    depth = ((((-1.82 * pow(10, -15) * p + 2.279 * pow(10, -10)) * p - 2.2512 * pow(10, -5)) * p + 9.72659) * p) / g
    print (depth)


###########################################################################################################

def writeSelected(SBE=False, P=False, RSBE=False, NETCDF=False):
    print("writing")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
    mainDir = dir_path

    os.chdir(dirName)
    cast = Cast()
    conn = create_connection(database)
    c = conn.cursor()
    c.execute("SELECT * FROM Casts")
    rows = c.fetchall()

    # Add a binary search to help improve runtime
    def binarySearch(arr, l, r, x):

        while l <= r:
            mid = l + (r - l) / 2;

            # Check if x is present at mid
            if arr[mid][0] == x:
                return mid

                # If x is greater, ignore left half
            elif arr[mid][0] < x:
                l = mid + 1

            # If x is smaller, ignore right half
            else:
                r = mid - 1

        # If we reach here, then the element
        # was not present
        print("error not in list/ordered")
        return -1


    for id in map.selectedIDs:
        index = binarySearch(rows, 0, len(rows) - 1, int(id))
        cast.id = rows[index][0]
        if int(id) == int(cast.id):
            cast.ShipName = rows[index][1]
            cast.ship = rows[index][2]
            cast.trip = rows[index][3]
            cast.station = rows[index][4]
            cast.Latitude = rows[index][5]
            cast.Longitude = rows[index][6]
            cast.SounderDepth = rows[index][7]
            cast.Instrument = rows[index][8]
            cast.InstrumentName = rows[index][9]
            cast.FishSet = rows[index][10]
            cast.CastType = rows[index][11]
            cast.comment = rows[index][12]
            cast.NumScans = rows[index][13]
            cast.SamplingRate = rows[index][14]
            cast.FileType = rows[index][15]
            cast.ChannelCount = rows[index][16]
            cast.DataChannels = rows[index][17]
            cast.Downcast = rows[index][18]
            cast.Subsample = rows[index][19]
            cast.MinDepth = rows[index][20]
            cast.MaxDepth = rows[index][21]
            cast.FishingStrata = rows[index][22]
            cast.metData = rows[index][23]
            cast.CastDatetime = rows[index][24]
            cast.File = rows[index][25]
            cast.Language = rows[index][26]
            cast.Encoding = rows[index][27]
            cast.Contact = rows[index][28]
            cast.Country = rows[index][29]
            cast.MaintenanceContact = rows[index][30]
            cast.OrgName = rows[index][31]
            cast.DataLimit = rows[index][32]
            # Creates a new folder and changes current working directory.
            os.chdir(mainDir)
            createFolder("Revised")
            print("Writing: " + cast.id.__str__())
            # Create Dataframe based on file type. SBE Data is stored in SBE_Data table, P File Data Stored in Data Table.
            # For SBE Files
            if (cast.File.lower().endswith("sbe")):
                if NETCDF:
                    continue
                df = pd.read_sql_query(
                    "select * from SBE_Data where SBE_Data.cid = (Select id from Casts where id = '{dv}') limit '{lmt}'".format(
                        dv=cast.id, lmt=cast.DataLimit),
                    conn)
            # For P Files
            else:
                df = pd.read_sql_query(
                    "select * from Data where Data.cid = (Select id from Casts where id = '{dv}') limit '{lmt}'".format(
                        dv=cast.id, lmt=cast.DataLimit), conn)
            # We dont want to print the cast id's and data id's over and over again in our data,
            # so we remove them from the data frame.
            df = df.drop('cid', 1)
            if not NETCDF:
                # Drop any columns with empty data, except for the netcdf's
                df = df.dropna(axis=1)
            try:
                # Remove did from the dataframe.
                df = df.drop('did', 1)
            except:
                # If did fails to remove, this means the data was pulled from the SBE Data table and not the P file table.
                df = df.drop('sid', 1)
            if SBE:
                # Original file was an SBE file.
                if cast.File.lower().endswith("sbe"):
                    # filename = cast.id.__str__() + "_DB.sbe"
                    filename = cast.id.__str__() + ".sbe"
                    # Creating the file name based on the deployment ID and the deployment date.
                    f = open(filename, "w+")
                    read = conn.cursor()
                    read.execute("SELECT Line FROM Header Where cid like '{castID}'".format(castID=cast.id))
                    header = read.fetchall()
                    for h in header:
                        f.writelines(h)
                        f.write("\n")
                    read.execute("SELECT Software_Info FROM Software Where cid like '{castID}'".format(castID=cast.id))
                    header = read.fetchall()
                    for h in header:
                        f.writelines(h)
                        f.write("\n")
                    read.execute(
                        "SELECT Instrument_Info FROM Instrument Where cid like '{castID}'".format(castID=cast.id))
                    header = read.fetchall()
                    for h in header:
                        f.writelines(h)
                        f.write("\n")
                    f.write("*END*\n")
                    df.to_string(f)
                    f.close()
                else:
                    # filename = cast.id.__str__() + "_P_DB.sbe"
                    filename = cast.id.__str__() + ".sbe"
                    # Creating the file name based on the deployment ID and the deployment date.
                    f = open(filename, "w+")
                    f.write("* " + cast.InstrumentName.__str__() + " Data File:" +
                            "\n* FileName = " + cast.File.__str__() +
                            "\n** VESSEL/TRIP/SEQ STN: " + cast.id.__str__() +
                            "\n** LATITUDE: " + cast.Latitude.__str__() +
                            "\n** LONGITUDE: " + cast.Longitude.__str__() +
                            "\n** SOUNDING DEPTH: " + cast.SounderDepth.__str__() +
                            "\n** PROBE TYPE: " + cast.Instrument.__str__() +
                            "\n** COMMENTS: " + cast.comment.__str__() +
                            "\n# start_time = " + cast.CastDatetime.__str__() + "\n")
                    read = conn.cursor()
                    read.execute("SELECT Line FROM Header Where cid like '{castID}'".format(castID=cast.id))
                    header = read.fetchall()
                    for h in header:
                        lin = "# " + h.__str__()
                        lin = lin.replace("(", "").replace(")", "").replace("'", "").replace(",", "").replace("\\n", "")
                        f.writelines(lin)
                        f.write("\n")
                    f.write("*END*\n")
                    df.to_string(f)
            if P:
                #filename = cast.id.__str__() + "_sbe_DB.p"
                filename = cast.id.__str__() + ".p"
                # Creating the file name based on the deployment ID and the deployment date.
                f = open(filename, "w+")
                if cast.File.lower().endswith("sbe"):
                    def DecimalDegrees_to_DegreesMins(lat, lon):
                        latDeg = lat[0:2]
                        lonDeg = lon[0:3]
                        latMins = lat[3:5]
                        lonMins = lon[4:5]
                        latMins = float(latMins) * 60
                        lonMins = float(lonMins) * 60
                        latMins = latMins.__str__().split(".")
                        if latMins[0].__len__() < 2:
                            latMins[0] = "0" + latMins[0]
                        if latMins[1].__len__() < 2:
                            latMins[1] = latMins[1] + "0"
                        lonMins = lonMins.__str__().split(".")
                        if lonMins[0].__len__() < 2:
                            lonMins[0] = "0" + lonMins[0]
                        if lonMins[1].__len__() < 2:
                            lonMins[1] = lonMins[1] + "0"
                        latMins = latMins[0] + "." + latMins[1]
                        lonMins = lonMins[0] + "." + lonMins[1]
                        cast.Latitude = latDeg + " " + latMins
                        cast.Longitude = lonDeg + " " + lonMins
                    DecimalDegrees_to_DegreesMins(cast.Latitude, cast.Longitude)
                    if cast.id.__str__().__len__() < 8:
                        num = 8 - cast.id.__str__().__len__()
                        for n in range(num):
                            cast.id = "0" + cast.id.__str__()
                    if cast.SounderDepth.__str__().__len__() < 4:
                        num = 4 - cast.SounderDepth.__str__().__len__()
                        for n in range(num):
                            cast.SounderDepth = "0" + cast.SounderDepth.__str__()
                    if cast.Instrument.__str__().__len__() < 5:
                        num = 5 - cast.Instrument.__str__().__len__()
                        for n in range(num):
                            cast.Instrument = " " + cast.Instrument.__str__()
                    if cast.comment.__str__().__len__() < 14:
                        num = 14 - cast.comment.__str__().__len__()
                        for n in range(num):
                            cast.comment = " " + cast.comment.__str__()
                    f.write(
                        cast.id.__str__() + "  " + cast.Latitude.__str__() + " " + cast.Longitude.__str__().replace("-",
                                                                                                                    "-0") + " " + cast.CastDatetime.__str__() + " " + cast.SounderDepth.__str__() + " " + cast.Instrument.__str__() + " " + cast.setNumber.__str__() + " " + cast.castType.__str__() + " " + cast.comment.__str__())
                    f.write("\n-- Data --\n")
                    df.to_string(f)
                    print("SBE")
                else:
                    # filename = cast.id.__str__() + "_P_DB.p"
                    filename = cast.id.__str__() + ".p"
                    f = open(filename, "w+")
                    read = conn.cursor()
                    read.execute("SELECT Line FROM Header Where cid like '{castID}'".format(castID=cast.id))
                    header = read.fetchall()
                    for h in header:
                        f.writelines(h)
                    f.write("-- DATA --")
                    df.to_string(f)
            if RSBE:
                # Look for any external Meteorological data
                if cast.File.lower().endswith("sbe"):
                    try:
                        # NOTE: Script requires _met.xlsx files in same directory as running script
                        loc = dir_path + "\\" + cast.ship.__str__() + cast.trip.__str__() + "_met.xlsx"
                        wb = xlrd.open_workbook(loc)
                        sheet = wb.sheet_by_index(0)
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
                else:
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
                filename = cast.id.__str__() + ".rsbe"
                # Creating the file name based on the deployment ID and the deployment date.
                f = open(filename, "w+")
                cmt = rows[index][12]
                f.write("** VESSEL/TRIP/SEQ STN: " + cast.id.__str__() +
                        "\n** VESSEL NAME: " + cast.ShipName.__str__() +
                        "\n** VESSEL NUMBER: " + cast.ship.__str__() +
                        "\n** TRIP NUMBER: " + cast.trip.__str__() +
                        "\n** STATION/SEQUENCE NUMBER: " + cast.station.__str__() +
                        "\n** LATITUDE: " + cast.Latitude.__str__() +
                        "\n** LONGITUDE: " + cast.Longitude.__str__() +
                        "\n** DATE: " + cast.CastDatetime.__str__() +
                        "\n** SOUNDING DEPTH: " + cast.SounderDepth.__str__() +
                        "\n** PROBE TYPE: " + cast.Instrument.__str__() +
                        "\n** PROBE NAME: " + cast.InstrumentName.__str__() +
                        "\n** SET NUMBER: " + cast.setNumber.__str__() +
                        "\n** CAST TYPE: " + cast.castType.__str__() +
                        "\n** NUMBER OF SCANS: " + cast.NumScans.__str__() +
                        "\n** SAMPLING RATE: " + cast.SamplingRate.__str__() +
                        "\n** CHANNEL COUNT: " + cast.channelCount.__str__() +
                        "\n** DATA CHANNELS: " + cast.dataChannels.__str__() +
                        "\n** DOWNCAST: " + cast.downcast.__str__() +
                        "\n** SUBSAMPLE: " + cast.subsample.__str__() +
                        "\n** MIN DEPTH: " + cast.minDepth.__str__() +
                        "\n** MAX DEPTH: " + cast.maxDepth.__str__() +
                        "\n** FISHING STRATA: " + cast.fishingStrata.__str__() +
                        "\n** METDATA: " + cast.metData.__str__() +
                        "\n** CLOUD: " + cast.Cloud.__str__() +
                        "\n** WIND DIRECTION: " + cast.WinDir.__str__() +
                        "\n** WIND SPEED: " + cast.WinSPD.__str__() +
                        "\n** WW CODE: " + cast.wwCode.__str__() +
                        "\n** BAR PRESSURE: " + cast.BarPres.__str__() +
                        "\n** TEMP WET: " + cast.TempWet.__str__() +
                        "\n** TEMP DRY: " + cast.TempDry.__str__() +
                        "\n** WAVE PERIOD: " + cast.WavPeroid.__str__() +
                        "\n** WAVE HEIGHT: " + cast.WavHeight.__str__() +
                        "\n** SWELL DIRECTION: " + cast.SwellDir.__str__() +
                        "\n** SWELL PERIOD: " + cast.SwellPeroid.__str__() +
                        "\n** SWELL HEIGHT: " + cast.SwellHeight.__str__() +
                        "\n** ICE CONCENTRATION: " + cast.IceConc.__str__() +
                        "\n** ICE STAGE: " + cast.IceStage.__str__() +
                        "\n** ICE BERGS: " + cast.IceBergs.__str__() +
                        "\n** LANGUAGE: " + cast.language.__str__() +
                        "\n** ENCODING: " + cast.encoding.__str__() +
                        "\n** POINT OF CONTACT: " + cast.PointOfContact.__str__() +
                        "\n** MAINTENANCE CONTACT: " + cast.MaintenanceContact.__str__() +
                        "\n** ORGANIZATION: " + cast.OrgName.__str__() +
                        "\n** COUNTRY: " + cast.Country.__str__() +
                        "\n** DATA LINES: " + cast.DataLimit.__str__() +
                        "\n** COMMENTS: " + cast.comment +
                        "\n** FILE TYPE: " + cast.filetype.__str__() +
                        "\n** FILE NAME: " + cast.File.__str__() +
                        "\n")
                read = conn.cursor()
                read.execute("SELECT Line FROM Header Where cid like '{castID}'".format(castID=cast.id))
                header = read.fetchall()
                if not cast.File.lower().endswith("sbe"):
                    for h in header:
                        lin = "# " + h.__str__()
                        lin = lin.replace("(", "").replace(")", "").replace("'", "").replace(",", "").replace("\\n", "")
                        f.writelines(lin)
                        f.write("\n")
                read.execute("SELECT Software_Info FROM Software Where cid like '{castID}'".format(castID=cast.id))
                header = read.fetchall()
                for h in header:
                    f.writelines(h)
                    f.write("\n")
                read.execute("SELECT Instrument_Info FROM Instrument Where cid like '{castID}'".format(castID=cast.id))
                header = read.fetchall()
                for h in header:
                    f.writelines(h)
                    f.write("\n")
                f.write("*END*\n")
                df.to_string(f)
            if NETCDF:
                if cast.File.lower().__contains__("p"):
                    ####################################################################################################
                    # NETCDF CREATION HERE:
                    ####################################################################################################
                    nc_outfile = cast.id.__str__() + ".nc"
                    nc_out = nc.Dataset(nc_outfile, 'w', format='NETCDF3_CLASSIC')
                    nc_out.Conventions = 'CF-1.6'
                    nc_out.title = 'AZMP netCDF file'
                    nc_out.institution = 'Northwest Atlantic Fisheries Centre, Fisheries and Oceans Canada'
                    nc_out.source = cast.File
                    nc_out.references = ''
                    nc_out.description = cast.comment
                    nc_out.created = 'Created ' + tt.ctime(tt.time())
                    # nc_out.processhistory = history
                    nc_out.trip_id = cast.id
                    nc_out.instrument_type = cast.InstrumentName
                    nc_out.instrument_ID = cast.Instrument
                    nc_out.shipname = cast.ShipName
                    nc_out.nafc_shipcode = cast.ship
                    nc_out.time_of_cast = cast.CastDatetime
                    nc_out.format_of_time = "YYYY-MM-DD HH:MM:SS"
                    # process histroy:
                    read = conn.cursor()
                    read.execute("SELECT Line FROM Header Where cid like '{castID}'".format(castID=cast.id))
                    header = read.fetchall()
                    # TODO: Filter history out of header if necessary.
                    history = []
                    # Here we are adding all header info into the history
                    for h in header:
                        history.append(h.__str__().replace('\n', '').replace('(', '').replace(')', '').replace("'", ''))
                    num_history_lines = np.size(history)
                    # NOTE: ERROR when trying to exec only with map
                    #for i in range(0, num_history_lines):
                        # exec ('nc_out.processhistory_' + str(i) + ' = ' + ' \' ' + history[i].replace('\n','') + ' \' ')
                    # Create dimensions
                    time = nc_out.createDimension('time', 1)
                    # level = nc_out.createDimension('level', len(df_temp.columns))
                    level = nc_out.createDimension('level', cast.DataLimit)
                    # Create coordinate variables
                    times = nc_out.createVariable('time', np.float64, ('time',))
                    levels = nc_out.createVariable('level', np.float32, ('level',))
                    # **** NOTE: Maybe consider using ID instead of time for dimension **** #
                    # Create 1D variables
                    latitudes = nc_out.createVariable('latitude', np.float32, ('time'), zlib=True)
                    longitudes = nc_out.createVariable('longitude', np.float32, ('time'), zlib=True)
                    sounder_depths = nc_out.createVariable('sounder_depth', np.float32, ('time'), zlib=True)
                    metdata = nc_out.createVariable('metdata', 'c', ('time'), zlib=True)
                    # Create 2D variables
                    temp = nc_out.createVariable('temperature', np.float32, ('level'), zlib=True, fill_value=-9999)
                    sal = nc_out.createVariable('salinity', np.float32, ('level'), zlib=True, fill_value=-9999)
                    cond = nc_out.createVariable('conductivity', np.float32, ('level'), zlib=True, fill_value=-9999)
                    sigt = nc_out.createVariable('sigma-t', np.float32, ('level'), zlib=True, fill_value=-9999)
                    o2 = nc_out.createVariable('oxygen', np.float32, ('level'), zlib=True, fill_value=-9999)
                    fluo = nc_out.createVariable('fluorescence', np.float32, ('level'), zlib=True, fill_value=-9999)
                    par = nc_out.createVariable('irradiance', np.float32, ('level'), zlib=True, fill_value=-9999)
                    ph = nc_out.createVariable('ph', np.float32, ('level'), zlib=True, fill_value=-9999)
                    # Variable Attributes
                    read = conn.cursor()
                    read.execute("SELECT * FROM Meteor Where cid like '{castID}'".format(castID=cast.id))
                    meteor = read.fetchall()
                    met = []
                    for m in meteor:
                        for n in m:
                            met.append(n)
                    metdata.cloud = met[2]
                    metdata.wind_direction = met[3]
                    metdata.wind_speed_kts = met[4]
                    metdata.WW_code = met[5]
                    metdata.BarometricPressure_mb = met[6]
                    metdata.Wet_air_temp = met[7]
                    metdata.Dry_air_temp = met[8]
                    metdata.Wave_period = met[9]
                    metdata.Wave_height = met[10]
                    metdata.Swell_direction = met[11]
                    metdata.Swell_height = met[12]
                    metdata.Ice_conc = met[13]
                    metdata.Ice_stage = met[14]
                    metdata.Icebergs = met[15]
                    latitudes.units = 'degree_north'
                    longitudes.units = 'degree_east'
                    times.units = 'hours since 1900-01-01 00:00:00'
                    times.calendar = 'gregorian'
                    levels.units = 'dbar'
                    levels.standard_name = "pressure"
                    levels.valid_min = 0
                    temp.units = 'Celsius'
                    temp.long_name = "Water Temperature"  # (may be use to label plots)
                    temp.standard_name = "sea_water_temperature"
                    sal.long_name = "Practical Salinity"
                    sal.standard_name = "sea_water_salinity"
                    sal.units = "1"
                    sal.valid_min = 0
                    sigt.standard_name = "sigma_t"
                    sigt.long_name = "Sigma-t"
                    sigt.units = "Kg m-3"
                    o2.long_name = "Dissolved Oxygen Concentration";
                    o2.standard_name = "oxygen_concentration";
                    o2.units = "ml L-1";
                    cond.long_name = "Water Conductivity";
                    cond.standard_name = "sea_water_conductivity";
                    cond.units = "S m-1";
                    fluo.long_name = "Chl-a Fluorescence";
                    fluo.standard_name = "concentration_of_chlorophyll_in_sea_water";
                    fluo.units = "mg m-3";
                    par.long_name = "Irradiance";
                    par.standard_name = "irradiance";
                    par.units = "umol photons m-2 s-1";
                    ph.long_name = "water PH";
                    ph.standard_name = "PH";
                    ph.units = "unitless";
                    # fill structure
                    # TODO: Check SBE Column names and extra P file columns
                    temp[:] = df["temp"].values
                    sal[:] = df["sal"].values
                    cond[:] = df["cond"].values
                    sigt[:] = df["sigt"].values
                    o2[:] = df["oxy"].values
                    fluo[:] = df["flor"].values
                    par[:] = df["par"].values
                    ph[:] = df["pH"].values
                    # Fill cast info
                    latitudes[:] = cast.Latitude
                    longitudes[:] = cast.Longitude
                    sounder_depths[:] = cast.SounderDepth
                    # Fill time
                    date = datetime.datetime.strptime(cast.CastDatetime, '%Y-%m-%d %H:%M:%S')
                    times[:] = nc.date2num(date, units=times.units, calendar=times.calendar)
                    Pbin = np.array(df['pres'])
                    levels[:] = Pbin
                    print('Done!')
                    nc_out.close()
    os.chdir(dirName)


###########################################################################################################


if __name__ == '__main__':
    # Create windows and frames
    root = Tk()
    root.title('Model Definition')
    root.geometry('{}x{}'.format(460, 350))
    database = "CTD.db"
    root.state('zoomed')
    top_frame = Frame(root, relief=SUNKEN, borderwidth=10, width=5, height=5)
    top_frame.pack(side=LEFT)
    side_frame = Frame(root, relief=SUNKEN, borderwidth=10, width=5, height=5)
    side_frame.pack(side=RIGHT)



    # create the widgets for the side frame
    text_label = Label(side_frame, text="Information", fg="red", font="Times")
    textBox = Text(side_frame, width=20, height=20)
    buttonReset = Button(side_frame, height=1, width=10, text="Reset", highlightcolor='red', highlightthickness=3,
                          command=lambda: resetMap())

    # create the widgets for the top frame
    ship_label = Label(top_frame, text="Ship", fg="red", font="Times")
    ShipBox = Entry(top_frame)
    trip_label = Label(top_frame, text="Trip", fg="red", font="Times")
    TripBox = Entry(top_frame)
    station_label = Label(top_frame, text="Station", fg="red", font="Times")
    StationBox = Entry(top_frame)
    year_lab = Label(top_frame, text="Year", fg="red", font="Times")
    YearBox = Entry(top_frame)
    month_lab = Label(top_frame, text="Month", fg="red", font="Times")
    MonthBox = Entry(top_frame)
    min_lat = Label(top_frame, text="Min Latitude", fg="red", font="Times")
    LatMinBox = Entry(top_frame)
    min_lon = Label(top_frame, text="Min Longitude", fg="red", font="Times")
    LongMinBox = Entry(top_frame)
    max_lat = Label(top_frame, text="Max Latitude", fg="red", font="Times")
    LatMaxBox = Entry(top_frame)
    max_lon = Label(top_frame, text="Max Longitude", fg="red", font="Times")
    LongMaxBox = Entry(top_frame)
    output_label = Label(top_frame, text="Output Format", fg="black", font="Times")
    output_line = Label(top_frame, text="-------------", fg="black", font="Times")

    # RSBE, SBE, P, NETCDF


    def selNetcdf():
        rsbe = False
        sbe = False
        p = False
        netcdf = True
        map.output = [rsbe,sbe,p,netcdf]

    def selRsbe():
        rsbe = True
        sbe = False
        p = False
        netcdf = False
        map.output = [rsbe, sbe, p, netcdf]

    def selSbe():
        rsbe = False
        sbe = True
        p = False
        netcdf = False
        map.output = [rsbe, sbe, p, netcdf]

    def selP():
        rsbe = False
        sbe = False
        p = True
        netcdf = False
        map.output = [rsbe, sbe, p, netcdf]


    v = IntVar()
    R1 = Radiobutton(top_frame, text="NETCDF", value=1, variable=v, command=lambda: selNetcdf())
    R2 = Radiobutton(top_frame, text="RSBE", value=2, variable=v,  command=lambda: selRsbe())
    R3 = Radiobutton(top_frame, text="SBE FILE", value=3, variable=v,  command=lambda: selSbe())
    R4 = Radiobutton(top_frame, text="P FILE", value=4, variable=v, command=lambda: selP())
    buttonSelect = Button(top_frame, height=1, width=10, text="Select", highlightcolor='red', highlightthickness=3,
                          command=lambda: retrieve_input(map))
    buttonWrite = Button(top_frame, height=1, width=10, text="Write", highlightcolor='red', highlightthickness=3,
                         command=lambda: writeSelected(RSBE=map.output[0], SBE=map.output[1], P=map.output[2], NETCDF=map.output[3]))


    fig = plt.figure(figsize=(2, 1))
    map = Map()
    print("Getting Points")
    map.getPoints()
    canvas = FigureCanvasTkAgg(fig, root)
    canvas.show
    print("showing")
    canvas.get_tk_widget().pack(side=tk.RIGHT, in_=root, fill=tk.BOTH, expand=False)
    toolbar = NavigationToolbar2TkAgg(canvas, root)
    # Set none to prevent canvas from moving on hover.
    toolbar.message = None
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # layout the widgets in the side frame
    text_label.grid(row=0, column=1)
    textBox.grid(row=1, column=1)
    textBox.yview_scroll(100000000, "units")
    textBox.insert(INSERT, "Files: " + "0" + "\n")
    buttonReset.grid(row=2, column=1)

    # layout the widgets in the top frame
    ship_label.grid(row=0, column=1)
    ShipBox.grid(row=1, column=1)
    trip_label.grid(row=2, column=1)
    TripBox.grid(row=3, column=1)
    station_label.grid(row=4, column=1)
    StationBox.grid(row=5, column=1)
    year_lab.grid(row=6, column=1)
    YearBox.grid(row=7, column=1)
    month_lab.grid(row=8, column=1)
    MonthBox.grid(row=9, column=1)
    min_lat.grid(row=10, column=1)
    LatMinBox.grid(row=11, column=1)
    min_lon.grid(row=12, column=1)
    LongMinBox.grid(row=13, column=1)
    max_lat.grid(row=14, column=1)
    LatMaxBox.grid(row=15, column=1)
    max_lon.grid(row=16, column=1)
    LongMaxBox.grid(row=17, column=1)
    buttonSelect.grid(row=18, column=1)
    buttonWrite.grid(row=18, column=2)
    output_label.grid(row=0, column=2)
    output_line.grid(row=1, column=2)
    R1.grid(row=2, column=2)
    R2.grid(row=4, column=2)
    R3.grid(row=6, column=2)
    R4.grid(row=8, column=2)

    def on_closing():
        root.destroy()
        exit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()