from Toolkits import ships_tk
from Toolkits import inst_tk
from Toolkits import dir_tk
import os
import sys

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

        # For IGOSS
        self.isTemperature = False
        self.isPressure = False
        self.isSalinity = False
        self.k1 = "8" # 7: Selected depths, 8: Significant
        self.k2 = "1" # 0: No salinity recorded, 1: 1 in situ sensor better than 0.02 PSU, 2: 1 in situ sensor less than 0.02 PSU, 3: sample analysis

        # For Trim
        self.Trim = []
        self.hasStart = False
        self.startpoint = None
        self.endpoint = None
        self.TrimmedData = []
        self.isTrimming = True




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

    return dateN


###########################################################################################################

# Stores all data in Cast object
def odf_meta(cast, datafile):
    f = open(datafile)
    filename = datafile.split("/")
    filename = filename[filename.__len__() - 1]
    cast.filename = filename
    filetype_v2 = False # bool to tell if file uses different format type
    isData = False
    xbt = False
    count = 0
    for line in f:
        count = count + 1
        if count == 879:
            print()

        if not isData:
            line = line.lstrip().rstrip().replace("'", "").replace(",", "").replace("\\", "")

        if isData:
            row = line.replace("\n", "").replace("'", "").lstrip().rstrip().split()
            cast.data.append(row)

        elif line.__contains__("MODEL="):
            cast.InstrumentName = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("SERIAL_NUMBER="):
            cast.Instrument = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("START_DATE_TIME="):
            nline = line.replace("\\", "").replace(",", "").replace("'", "").split("=")[1].split()[0].split("-")
            time = line.replace("\\", "").replace(",", "").replace("'", "").split("=")[1].split(" ")[1]
            day = nline[0]
            month = nline[1]
            year = nline[2]
            tempdate = [month, day, year, time]
            cast.CastDatetime = convertDate(cast, tempdate)

        elif line.__contains__("INITIAL_LATITUDE="):
            lat = line.split("=")[1].replace(",", "")
            deg = lat.split(".")[0]
            min = lat.split(".")[1]
            lat = [deg, min]
            cast.Latitude = convertDecimalDeg_to_DegMin(lat)

        elif line.__contains__("INITIAL_LONGITUDE="):
            lon = line.split("=")[1].replace(",", "")
            deg = lon.split(".")[0]
            min = lon.split(".")[1]
            lon = [deg, min]
            cast.Longitude = convertDecimalDeg_to_DegMin(lon)

        elif line.__contains__("CRUISE_NUMBER="):
            nline = line.split("=")[1].replace(",", "").lstrip().rstrip()
            cast.ShipName = nline[0:3]
            getShipNumber(cast)
            cast.trip = nline[-3:]
            print()

        elif line.__contains__("EVENT_NUMBER="):
            cast.station = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("SOUNDING="):
            cast.SounderDepth = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("EVENT_COMMENTS="):
            cast.comment = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("ORGANIZATION="):
            cast.OrgName = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("CHIEF_SCIENTIST="):
            cast.PointOfContact = line.split("=")[1].lstrip().rstrip()

        elif line.__contains__("-- DATA --"):
            isData = True

        if line.__contains__("PROCESS=*"):
            nline = line.replace("PROCESS=", "")
            cast.software.append(nline)

        if line.__contains__("PROCESS=**"):
            nline = line.replace("PROCESS=", "")
            cast.userInput.append(nline)

        if line.__contains__("PROCESS=#"):
            nline = line.replace("PROCESS=", "")
            cast.InstrumentInfo.append(nline)

###########################################################################################################

def getInstrumentName(cast, instDF=inst_tk.createInstrumentDF()):

    number = ''.join(c for c in cast.Instrument if c.isdigit())
    i = instDF[instDF[1].str.match(number)]
    try:
        iname = i.values[0][0]
        cast.InstrumentName = iname
    except Exception as e:
        print(e.__str__())
        print("Cannot Find Instrument name in file...\nSetting Instrument Name to Instrument Number: " + cast.Instrument)
        cast.InstrumentName = cast.Instrument

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

# Convert Lat / Long from Decimal Deg to Degree Min
def convertDecimalDeg_to_DegMin(convert):
    deg = convert[0].lstrip().rstrip()
    min = "." + convert[1].lstrip().rstrip()
    min = float(min)
    min = min *60
    #min = float("{0:.2f}".format(min))*60
    result = deg.__str__()+ " " + min.__str__()
    return result

###########################################################################################################

def getShipName(cast, shipDF=ships_tk.createShipDF()):
    try:
        s = shipDF[shipDF[0].str.match(cast.ship.__str__())]
        sname = s.values[0][2]
        cast.ShipName = sname
    except Exception as e:
        cast.ShipName = "xxx"
        print(e.__str__())
        print(
            "Cannot Find Ship Name In File...")

###########################################################################################################

def getShipNumber(cast, shipDF=ships_tk.createShipDF()):

    try:
        s = shipDF[shipDF[2].str.match(cast.ShipName.__str__())]
        snumber = s.values[0][0]
        cast.ship = snumber
    except Exception as e:
        cast.ship = "00"
        print(e.__str__())
        print(
            "Cannot Find Ship Number In File...")

###########################################################################################################