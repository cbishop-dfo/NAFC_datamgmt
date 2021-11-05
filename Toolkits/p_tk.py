import sqlite3
import re
import numpy as np
import pandas as pd
import datetime
import xlrd
import os
import seawater as sw
from Toolkits import dir_tk
from Toolkits import ships_tk
from Toolkits import inst_tk

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


###########################################################################################################


def getChannelInfo(cast, datafile):

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

def pfile_to_dataframe(cast, filename):
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
                if not line == "":
                    cast.data.append(line.split(' '))

    # Read columns & remove last line of header
    cast.columns = cast.header[-1]
    cast.header = cast.header[:-1]

    #d = cast.data[0]

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
    """
    #allColumns = ["scan", "pres", "depth", "temp", "cond", "sal", "sigt", "oxy", "flor", "par", "pH", "trp", "tra",
    #            "wet"]
    allColumns = cast.columns.split()
    cast.ColumnNames = allColumns

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
            dir_path = os.path.dirname(os.path.realpath(__file__))
            dirName = dir_path
            os.chdir(dirName)
            dir_tk.createProblemFolder()
            newfile = filename.__str__() + "_errorIndex"
            f = open(newfile, "w+")
            for h in cast.header:
                f.writelines(h)
            colNames = ""
            for c in cast.ColumnNames:
                colNames = colNames + "   " + c
            f.write(colNames)
            f.write("\n" + e.__str__())
            break
            #continue

    for column in Dictionary:
        try:
            df[column] = Dictionary[column]
        except Exception as e:
            print(e.__str__())
            df[column] = np.nan
    return df

###########################################################################################################


def read_pFile(cast, datafile):
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


def pfile_meta(cast, datafile):

    line = cast.header[1]
    nextLine = cast.header[2]
    lastLine = cast.header[3]
    cast.ship = line[0:2]
    cast.trip = line[2:5]
    cast.station = line[5:8]
    cast.id = int(cast.ship.__str__() + cast.trip.__str__() + cast.station.__str__())

    lat = line[9:18]
    long = line[18:30]
    cast.Latitude = lat #convertLatLong(lat)
    cast.Longitude = long.replace("-0", "-") #convertLatLong(long)

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

    getInstrumentName(cast)
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
def depthDF_to_PresDF(cast, df):
    presArray = []
    cast.Latitude = convertLatLong(cast.Latitude.lstrip().rstrip().split(" "))
    cast.Longitude = convertLatLong(cast.Longitude.lstrip().rstrip().split(" "))
    for d in df.values:
        pres = calculatePress(float(d[1]), float(cast.Latitude))
        presArray.append(pres)
    df["pres"] = presArray
    return df

###########################################################################################################

def calculateDepth(press, latitude):
    depth = sw.dpth(press, latitude)
    return depth

###########################################################################################################

def calculatePress(depth, latitude):
    press = sw.pres(depth, latitude)
    return press

###########################################################################################################

def getCastType(cast):
    if cast.castType == "":
        numOfCols = cast.ColumnNames.__len__()
        # less than 3 data columns is XBT (Vertical)
        if numOfCols <= 3:
            cast.castType = "V"
            return
        # Greater than 8 is Vertical
        elif numOfCols >= 8:
            cast.castType = "V"
            return
        # Else assume tow
        else:
            cast.castType = "T"
            return

###########################################################################################################

def getShipName(cast, shipDF=ships_tk.createShipDF()):
    s = shipDF[shipDF[0].str.match(cast.ship.__str__())]
    sname = s.values[0][2]
    cast.ShipName = sname

###########################################################################################################

# Use for SBE or RSBE in future if met data is decided to be added to other files besides the p files
def read_met_file(cast):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
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
# For use with database, checks if file is already in the database.
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

def getInstrumentName(cast, instDF=inst_tk.createInstrumentDF()):
    try:
        number = ''.join(c for c in cast.Instrument if c.isdigit())
        i = instDF[instDF[1].str.match(number)]
        iname = i.values[0][0]
        cast.InstrumentName = iname
    except:
        print("Instrument Number Not In Instrument Dataframe...\nNo Instrument Name Assigned.")

###########################################################################################################

def convertDate(cast, date):

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

def writeCNV(cast, df, datafile):
    newfile = datafile.split(".")[0] + ".cnv"
    filename = datafile.split("/")
    filename = filename[filename.__len__() - 1]
    writer = open(newfile, "w+")
    writer.write("* " + cast.InstrumentName + " Data File\n" +
                 "* Filename = " + filename + "\n")
    try:
        for QA in cast.QA:
            writer.write(QA + "\n")
    except:
        print("QA Not Applied")

    writer.write("** VESSEL/TRIP/SEQ STN: " + cast.id.__str__() +
            #"\n** VESSEL NAME: " + cast.ShipName.__str__() +
            #"\n** VESSEL NUMBER: " + cast.ship.__str__() +
            #"\n** TRIP NUMBER: " + cast.trip.__str__() +
            #"\n** STATION/SEQUENCE NUMBER: " + cast.station.__str__() +
            "\n** LATITUDE: " + cast.Latitude.__str__() +
            "\n** LONGITUDE: " + cast.Longitude.__str__() +
            "\n** DATE: " + cast.CastDatetime.__str__() +
            "\n** SOUNDING DEPTH: " + cast.SounderDepth.__str__() +
            "\n** PROBE TYPE: " + cast.Instrument.__str__() +
            #"\n** PROBE NAME: " + cast.InstrumentName.__str__() +
            "\n** CTD NUMBER: " + cast.setNumber.__str__() +
            "\n** CAST TYPE: " + cast.castType.__str__() +
            #"\n** CAST TYPE: " + cast.castType.__str__() +
            #"\n** NUMBER OF SCANS: " + cast.NumScans.__str__() +
            #"\n** SAMPLING RATE: " + cast.SamplingRate.__str__() +
            #"\n** CHANNEL COUNT: " + cast.channelCount.__str__() +
            #"\n** DATA CHANNELS: " + cast.dataChannels.__str__() +
            #"\n** DOWNCAST: " + cast.downcast.__str__() +
            #"\n** SUBSAMPLE: " + cast.subsample.__str__() +
            #"\n** MIN DEPTH: " + cast.minDepth.__str__() +
            #"\n** MAX DEPTH: " + cast.maxDepth.__str__() +
            #"\n** FISHING STRATA: " + cast.fishingStrata.__str__() +
            #"\n** METDATA: " + cast.metData.__str__() +
            #"\n** CLOUD: " + cast.Cloud.__str__() +
            #"\n** WIND DIRECTION: " + cast.WinDir.__str__() +
            #"\n** WIND SPEED: " + cast.WinSPD.__str__() +
            #"\n** WW CODE: " + cast.wwCode.__str__() +
            #"\n** BAR PRESSURE: " + cast.BarPres.__str__() +
            #"\n** TEMP WET: " + cast.TempWet.__str__() +
            #"\n** TEMP DRY: " + cast.TempDry.__str__() +
            #"\n** WAVE PERIOD: " + cast.WavPeroid.__str__() +
            #"\n** WAVE HEIGHT: " + cast.WavHeight.__str__() +
            #"\n** SWELL DIRECTION: " + cast.SwellDir.__str__() +
            #"\n** SWELL PERIOD: " + cast.SwellPeroid.__str__() +
            #"\n** SWELL HEIGHT: " + cast.SwellHeight.__str__() +
            #"\n** ICE CONCENTRATION: " + cast.IceConc.__str__() +
            #"\n** ICE STAGE: " + cast.IceStage.__str__() +
            #"\n** ICE BERGS: " + cast.IceBergs.__str__() +
            #"\n** LANGUAGE: " + cast.language.__str__() +
            #"\n** ENCODING: " + cast.encoding.__str__() +
            #"\n** POINT OF CONTACT: " + cast.PointOfContact.__str__() +
            #"\n** MAINTENANCE CONTACT: " + cast.MaintenanceContact.__str__() +
            #"\n** ORGANIZATION: " + cast.OrgName.__str__() +
            #"\n** COUNTRY: " + cast.Country.__str__() +
            #"\n** DATA LINES: " + cast.DataLimit.__str__() +
            "\n** COMMENTS: " + cast.comment +
            #"\n** FILE TYPE: " + cast.filetype.__str__() +
            #"\n** FILE NAME: " + cast.File.__str__() +
            "\n")

    count = 0
    df = df.dropna(axis=1)
    for c in df:
        writer.write("# name " + count.__str__() + " = " + c + "\n")
        count = count + 1
    writer.write("*END*\n")
    writer.write(df.to_string(header=False, index=False))
###########################################################################################################

def writeCNV_With_MET(cast, df, datafile):
    newfile = datafile.split(".")[0] + ".sCTD"
    filename = datafile.split("/")
    filename = filename[filename.__len__()-1]
    writer = open(newfile, "w+")
    writer.write("* " + cast.InstrumentName + " Data File\n" +
                 "* Filename = " + filename + "\n")
    try:
        for QA in cast.QA:
            writer.write(QA + "\n")
    except:
        print("QA Not Applied")

    writer.write("** VESSEL/TRIP/SEQ STN: " + cast.id.__str__() +
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
            "\n** CTD NUMBER: " + cast.setNumber.__str__() +
            "\n** CAST TYPE: " + cast.castType.__str__() +
            "\n** NUMBER OF SCANS: " + cast.NumScans.__str__() +
            "\n** SAMPLING RATE: " + cast.SamplingRate.__str__() +
            "\n** CHANNEL COUNT: " + cast.channelCount.__str__() +
            "\n** DATA CHANNELS: " + cast.dataChannels.__str__() +
            "\n** DOWNCAST: " + cast.downcast.__str__() +
            "\n** SUBSAMPLE: " + cast.subsample.__str__() +
            "\n** MIN DEPTH: " + cast.minDepth.__str__() +
            "\n** MAX DEPTH: " + cast.maxDepth.__str__() +
            #"\n** FISHING STRATA: " + cast.fishingStrata.__str__() +
            #"\n** METDATA: " + cast.metData.__str__() +
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
            #"\n** FILE TYPE: " + cast.filetype.__str__() +
            #"\n** FILE NAME: " + cast.File.__str__() +
            "\n")

    count = 0
    df = df.dropna(axis=1)
    for c in df:
        writer.write("# name " + count.__str__() + " = " + c + "\n")
        count = count + 1
    writer.write("*END*\n")
    writer.write(df.to_string(header=True, index=False))


###########################################################################################################
def rewritePFile(cast, df, datafile):
    newfile = datafile.__str__() + "_modified"
    f = open(newfile, "w+")
    df = df.dropna(axis=1)

    for h in cast.header:
        f.writelines(h)
    colNames = ""
    for c in cast.ColumnNames:
        colNames = colNames + "   " + c
    f.write(colNames)
    f.write("\n")
    f.write("-- DATA --\n")
    f.write(df.to_string(header=False, index=False))

###########################################################################################################

def drop_non_pfile(cast, df):
    p_df = pd.DataFrame()
    """ 
    XBT  scan depth temp pres cond sal sigt
    CNV scan pres temp cond sal sigt oxy flor par ph trp tra wet
    
    NOTE: If cast was created from cnv_tk, cast.isXBT will either be true or undefined
    """

    for c in df:
        if c == "Pressure":
            p_df["pres"] = df[c]
            getChannelStats(cast, p_df, "pres")

        elif c == "Depth":
            p_df["depth"] = df[c]
            getChannelStats(cast, p_df, "depth")

        elif c == "Temperature":
            p_df["temp"] = df[c]
            getChannelStats(cast, p_df, "temp")

        elif c == "scan":
            p_df["scan"] = df[c]
            getChannelStats(cast, p_df, "scan")

        elif c == "Conductivity":
            p_df["cond"] = df[c]
            getChannelStats(cast, p_df, "cond")

        elif c == "Salinity":
            p_df["sal"] = df[c]
            getChannelStats(cast, p_df, "sal")

        elif c == "Density":
            p_df["sigt"] = df[c]
            getChannelStats(cast, p_df, "sigt")

        elif c == "Oxygen":
            p_df["oxy"] = df[c]
            getChannelStats(cast, p_df, "oxy")

        elif c == "Fluorescence":
            p_df["flor"] = df[c]
            getChannelStats(cast, p_df, "flor")

        elif c == "Photosynthetic Active Radiation":
            p_df["par"] = df[c]
            getChannelStats(cast, p_df, "par")

        elif c == "pH":
            p_df["ph"] = df[c]
            getChannelStats(cast, p_df, "ph")

        elif c == "Transmissometer attenuation":
            p_df["tra"] = df[c]
            getChannelStats(cast, p_df, "tra")

        elif c == "Transmissometer transmission":
            p_df["trp"] = df[c]
            getChannelStats(cast, p_df, "trp")

        elif c == "CDOM Fluorescence":
            p_df["wet"] = df[c]
            getChannelStats(cast, p_df, "wet")

    return p_df

###########################################################################################################

def getChannelStats(cast, df, c):
    localmax = max(df[c]).__str__()
    localmin = min(df[c]).__str__()
    cstat = '{:<10s}{:>20s}{:>20s}{:>20s}'.format("# span ", c.__str__() + " = ", localmin + ", ", localmax)
    cast.channel.append(cstat)

###########################################################################################################

def write_pfile(cast, df):
    # Line one in header
    cid = cast.ship.__str__() + cast.trip.__str__() + cast.station.__str__()
    lat = cast.Latitude.__str__()
    lon = cast.Longitude.__str__()
    date = cast.CastDatetime.split(" ")[0]
    time = cast.CastDatetime.split(" ")[1]
    soundDepth = cast.SounderDepth
    inst = cast.Instrument
    setNum = cast.setNumber
    cType = cast.castType
    comment = cast.comment

    # Line two in header
    numScans = df.values.__len__()

    # add checks for spacing issues and null values
    if lat.__len__() > 8:
        lat = lat[0:8]
    elif lat.__len__() < 8:
        n = 8 - int(lat.__len__())
        for i in range(n):
            lat = lat + "0"

    if lon.__len__() > 8:
        # TODO: if negative go to 9 if positive go to 8
        lon = lon[0:9]
    elif lon.__len__() < 8:
        n = 8 - int(lon.__len__())
        for i in range(n):
            lon = lon + "0"

    if time.__len__() > 4:
        time = time[0:5]

    line1 = cid + " " + lat + " " + lon + " " + date + " " + time + " " + soundDepth + " " + inst + " " + setNum + " " + cType + " " + comment + "\n"
    line2 = cid + "\n"
    line3 = cid + "\n"

    year = date.split("-")[0]
    filename = cid + ".p" + year
    writer = open(filename, "w+")
    writer.writelines("NAFC_Y2K_HEADER\n")
    writer.writelines(line1)
    writer.writelines(line2)
    writer.writelines(line3)

    writer.writelines("-- CHANNEL STATS -->\n")
    for c in cast.channel:
        writer.writelines(c + "\n")
    writer.writelines("-- END --\n")

    for name in df:
        writer.write(name + "    ")

    writer.writelines("\n-- DATA --\n")
    writer.write(df.to_string(header=False, index=False))