import numpy as np
import pandas as pd
import math
import seawater as sw
import datetime
import time as tt
from Toolkits import ships_tk
from Toolkits import inst_tk
try:
    import netCDF4 as nc
except:
    pass
"""
Toolkit for creating cast object types from cnv files
cnv_to_dataframe: dynamically creates a pandas dataframe based on the fields within the datafile
cnv_meta: Populates the fields within the Cast object

Required Toolkits:
ships_tk
inst_tk

Created By: Dylan Kennedy
03-05-2020
"""

class Cast(object):
    """
    Cast object used for storing both metadata and physical data
    """

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
        self.triptag = ""
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


def getFilename(datafile):
    path = datafile.replace("\\", "/").split("/")
    return path[path.__len__() - 1]


###########################################################################################################

def calculateDepth(press, latitude):
    """
    Converts pressure to depth

    :param press: sensor pressure (float)
    :param latitude: Latitude from metadata (float)
    :return: depth
    """
    """
    x = math.pow(math.sin(latitude/57.29578), 2)
    g = 9.780318*(1*(5.2788*math.pow(10, -3)+2.36*math.pow(10, -5)*x)*x)+1.092*math.pow(10, -6)*press

    depth = ((((-1.82*math.pow(10, -15)* press +2.279*math.pow(10,-10))
               *press-2.2512*math.pow(10,-5))
               *press+9.72659)*press)/g

    return depth
    """
    depth = sw.dpth(float(press), float(latitude))
    return depth

###########################################################################################################

def calculatePress(depth, latitude):
    """
    Converts depth to pressure

    :param depth: sensor depth (float)
    :param latitude: Latitude from metadata (float)
    :return: pressure
    """
    """
    x = math.pow(math.sin(latitude / 57.29578), 2)
    partial_g = 9.780318 * (1 * (5.2788 * math.pow(10, -3) + 2.36 * math.pow(10, -5) * x) * x)+1.092*math.pow(10, -6)

    press = ((((-1.82*math.pow(10, -15) +2.279*math.pow(10,-10))
               -2.2512*math.pow(10,-5))
               +9.72659))/(depth*partial_g)

    return press
    """
    press = sw.pres(float(depth), float(latitude))
    return press

###########################################################################################################

def setInstrumentInfo(cast, df, c, count):

    """
    Set instrument/sensor metadata

    :param cast: Cast Object
    :param df: Cast Dataframe
    :param c: column name
    :param count: index number
    :return:
    """
    localmax = max(df[c]).__str__()
    localmin = min(df[c]).__str__()
    name = "# name " + count.__str__() + " = " + c.__str__()
    # cstat = '{:<10s}{:>20s}{:>20s}{:>20s}'.format("# span ", c.__str__() + " = ", localmin + ", ", localmax)
    cast.InstrumentInfo.append(name)


###########################################################################################################

def setSpanInfo(cast, df):
    """
    :param cast: Cast Object
    :param df: Cast Dataframe
    :return:
    """
    for c in df:
        localmax = max(df[c]).__str__()
        localmin = min(df[c]).__str__()
        cstat = '{:<10s}{:>20s}{:>20s}{:>20s}'.format("# span ", c.__str__() + " = ", localmin + ", ", localmax)
        cast.InstrumentInfo.append(cstat)


###########################################################################################################

def fixColumnNames(cast, df):
    cast.ColumnNames = []
    cast.InstrumentInfo = []
    count = 0
    for c in df:
        cast.ColumnNames.append(c)
        setInstrumentInfo(cast, df, c, count)
        count = count + 1

###########################################################################################################

def cnv_ascii(cast):
    """
    Creates basic ascii file containing cast metadata

    :param cast: Cast Object
    :return:
    """
    asciiName = cast.ship.__str__() + cast.trip.__str__() + ".txt"
    try:
        # if read fails this indicates we need to create col names via exception.
        reader = open(asciiName, "r")
        writer = open(asciiName, "a+")
        writer.write(cast.ship.__str__() + ", "
                     + cast.trip.__str__() + ", "
                     + cast.Latitude.__str__() + ", "
                     + cast.Longitude.__str__() + ", "
                     + cast.CastDatetime.__str__() + "\n")

    except Exception as e:
        writer = open(asciiName, "a+")
        writer.write("Ship, Trip, Latitude, Longitude, Time\n")
        writer.write(cast.ship.__str__() + ", "
                     + cast.trip.__str__() + ", "
                     + cast.Latitude.__str__() + ", "
                     + cast.Longitude.__str__() + ", "
                     + cast.CastDatetime.__str__() + "\n")



###########################################################################################################

# Stores all data in Cast object
def cnv_meta(cast, datafile):
    """
    Stores all data in Cast object

    :param cast: Cast Object
    :param datafile: filename
    :return:
    """
    f = open(datafile)
    filename = datafile.split("/")
    filename = filename[filename.__len__() - 1]
    cast.filename = filename
    filetype_v2 = False # bool to tell if file uses different format type
    isData = False
    xbt = False

    for line in f:
        line = line.replace("\n", "")
        if isData:
            cast.data.append(line.replace("\n", "").lstrip().rstrip().split())
        if line.__contains__("System UpLoad Time"):
            filetype_v2 = True
            tempdate = line.split("=")[1].split()
            convertDate(cast, tempdate)
        elif line.__contains__("** ") or line.__contains__("**"):
            cast.userInput.append(line)
            if line.upper().__contains__("VESSEL"):
                if filetype_v2 or xbt:
                    line = line.replace("-", "_")
                    l = line.split(":")[1].lstrip().rstrip().split("_")
                    # Some files contain ship name in line, some use ship number
                    if l[0].isnumeric():
                        cast.ship = l[0][0:2]
                        cast.trip = l[0][2:5]
                        cast.station = l[0][5:]
                    else:
                        cast.ShipName = l[0][:-3].lower()
                        getShipNumber(cast)
                        cast.trip = l[0][-3:]
                        cast.station = l[2]
                elif line.__contains__("_"):
                    l = line.split(":")[1].split("_")
                    cast.ship = l[0][0:4]
                    cast.trip = l[0][4:7]
                    cast.station = l[2]

                else:
                    cast.id = line.split(':')[1].lstrip().rstrip()
                    cast.ship = cast.id[0:2]
                    cast.trip = cast.id[2:5]
                    cast.station = cast.id[5:8]

            elif line.upper().__contains__("DATE"):
                l = line.split()
                cast.CastDatetime = l[2] + " " + l[3]

            elif line.upper().__contains__("LATITUDE") or line.upper().__contains__("LAT"):
                try:
                    line = line.lower().replace("n", "")
                    lat = line.split(":")[1].lstrip().rstrip()
                    if lat.__len__() >= 5 and not lat.__contains__(" "):
                        x = lat[0:2]
                        y = lat[2:4] + "." + lat[4:]
                        lat = x + " " + y
                    cast.Latitude = convertLatLong(lat.split())
                except Exception as e:
                    print("Error Reading Longitude: " + e.__str__() + "\nLine: " + line.__str__())
            elif line.upper().__contains__("LONGITUDE") or line.upper().__contains__("LON"):
                try:
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
                except Exception as e:
                    print("Error Reading Longitude: " + e.__str__() + "\nLine: " + line.__str__())
            elif line.upper().__contains__("SOUNDING"):
                cast.SounderDepth = line.split(":")[1]
            elif line.upper().__contains__("COMMENTS"):
                cast.comment = line.split(":")[1]
            elif line.upper().__contains__("TRIP TAG"):
                cast.triptag = line.split(":")[1].lstrip().rstrip()
            elif line.upper().__contains__("CAST TYPE"):
                cast.castType = line.split(":")[1].lstrip().rstrip()
            elif line.upper().__contains__("PROBE"):
                if xbt:
                    cast.InstrumentName = line.split(":")[1].strip()
                else:
                    cast.Instrument = line.split(":")[1]
            elif line.upper().__contains__("VNET"):
                cast.VNET = line.split(":")[1]
            elif line.upper().__contains__("XBT NUMBER"):
                cast.Instrument = line.split(":")[1]
            elif line.upper() == "YEAR":
                year = line.split(":")[1].rstrip().lstrip()
            elif line.upper() == "MONTH":
                month = line.split(":")[1].rstrip().lstrip()
            elif line.upper() == "DAY":
                day = line.split(":")[1].rstrip().lstrip()
            elif line.upper() == "HOURS/MIN":
                time = line.split(":")[1].rstrip().lstrip()
                time = time[0:2] + ":" + time[2:4]
                casttime = year + "-" + month + "-" + day + " " + time
                cast.CastDatetime = casttime
            elif line.upper() == "FORMAT":
                cast.castType = line.split(":")[1]

        elif line.startswith("* "):
            if line.upper().__contains__("XBT"):
                xbt = True
                # Setting permanent var here because it explicitly states it's an XBT
                cast.isXBT = True
            cast.software.append(line)
        elif line.startswith("# "):
            cast.InstrumentInfo.append(line)
            if line.lower().__contains__("start_time"):
                dateArray = []
                date = line.split("=")[1].split()
                convertDate(cast, date)
        else:
            isData = True
    getShipName(cast)
    if not xbt:
        getInstrumentName(cast)

###########################################################################################################

def getInstrumentName(cast, instDF=inst_tk.createInstrumentDF()):
    """
    Assigns instrument name to cast object based in instrument number

    :param cast: Cast Object
    :param instDF: instrument dataframe created from the inst_tk
    :return:
    """

    number = ''.join(c for c in cast.Instrument if c.isdigit())
    i = instDF[instDF[1].str.match(number)]
    try:
        iname = i.values[0][0]
        cast.InstrumentName = iname
    except Exception as e:
        print(e.__str__())
        print("Cannot Find Instrument name in file...\nSetting Instrument Name to Instrument Number: " + cast.Instrument)
        cast.InstrumentName = cast.Instrument

"""
    # old method
    try:
        dfs = pd.read_excel(refFile, sheet_name="Sheet1")
    except:
        try:
            dfs = pd.read_excel("../Resources/CTD Instrument Info.xlsx", sheet_name="Sheet1")
        except:
            dfs = pd.read_excel("Resources/CTD Instrument Info.xlsx", sheet_name="Sheet1")


    for i in dfs.index:
        if cast.Instrument.__contains__(dfs['Serial Number (SN)'][i].__str__()):
            cast.InstrumentName = dfs['Instrument Type (SBE-CTD)'][i]
"""

###########################################################################################################

def getShipName(cast, shipDF=ships_tk.createShipDF()):
    """
    Assigns ship name to cast object based on ship number in cast

    :param cast: Cast Object
    :param shipDF: Ship dataframe created from the ships_tk
    :return:
    """
    try:
        s = shipDF[shipDF[0].str.match(cast.ship.__str__())]
        sname = s.values[0][2]
        cast.ShipName = sname
    except Exception as e:
        cast.ShipName = "xxx"
        print(e.__str__())
        print("Cannot Find Match Given Ship Number...")
        print("Ship Number: " + cast.ship.__str__())

###########################################################################################################

def getShipNumber(cast, shipDF=ships_tk.createShipDF()):
    """
    Assigns ship number to cast object based on ship name in cast

    :param cast: Cast Object
    :param shipDF: Ship dataframe created from the ships_tk
    :return:
    """

    try:
        s = shipDF[shipDF[2].str.match(cast.ShipName.__str__())]
        snumber = s.values[0][0]
        cast.ship = snumber
    except Exception as e:
        cast.ship = "00"
        print(e.__str__())
        print("Cannot Find Match Given Ship Name...")
        print("Ship Name: " + cast.ShipName.__str__())

###########################################################################################################


# Convert Lat / Long into decimals
def convertLatLong(convert):
    """
    Converts Lat/Lon into decimal degrees

    :param convert: array containing split latitude or longitude values
    :return: decimal degrees (float)
    """
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

# Dynamically creates a data frame based on the columns provided in the datafile, returns the data frame
def cnv_to_dataframe(cast):
    """
    Dynamically creates a data frame based on the columns provided in the datafile, returns the data frame

    :param cast: Cast Object (already populated)
    :return: CTD Dataframe
    """

    df = pd.DataFrame()
    allColumns = []
    for n in cast.InstrumentInfo:
        if n.__contains__("name"):
            col = n.split()
            allColumns.append(col[4].replace(":", ""))



    Dictionary = {}
    for c in allColumns:
        Dictionary[c] = []
        cast.ColumnNames.append(c)

    for dat in cast.data:
        try:
            index = 0
            for i in allColumns:
                Dictionary[i].append(dat[index])
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

# Dynamically creates a data frame based on the columns provided in the datafile, returns the data frame
def df_press_depth(cast):
    """
    Creates a dataframe containing both a preassure and a depth column

    :param cast: Cast Object (already populated)
    :return: Dataframe containing both presassure and depth
    """

    df = pd.DataFrame()
    allColumns = []
    colNumber = -1
    hasPress = False
    pressIndex = -1
    hasDepth = False
    depthIndex = -1
    for n in cast.InstrumentInfo:
        if n.__contains__("name"):
            colNumber = colNumber + 1
            if n.lower().__contains__("depth"):
                hasDepth = True
                depthIndex = colNumber
            if n.lower().__contains__("pressure"):
                hasPress = True
                pressIndex = colNumber
            col = n.split()
            allColumns.append(col[4].replace(":", ""))

    #TODO: FIX NAME POSITION IN HEADER

    # Add Depth Column
    if hasPress and not hasDepth:
        colNumber = colNumber + 1
        cast.InstrumentInfo.append("# name " + colNumber.__str__() +" = depSM: Depth [salt water, m]")
        allColumns.append("depSM")
    # Add Pressure Column
    if hasDepth and not hasPress:
        colNumber = colNumber + 1
        cast.InstrumentInfo.append("# name " + colNumber.__str__() + " = prDM: Pressure, Digiquartz [db]")
        allColumns.append("prDM")


    Dictionary = {}
    for c in allColumns:
        Dictionary[c] = []
        cast.ColumnNames.append(c)

    for dat in cast.data:
        try:
            index = 0
            for i in allColumns:
                Dictionary[i].append(dat[index])
                index = index + 1

        except Exception as e:
            try:
                if depthIndex > -1:
                    d = dat[depthIndex]
                    press = calculatePress((float(d)), cast.Latitude)
                    Dictionary[i].append(press)
                if pressIndex > -1:
                    p = dat[pressIndex]
                    dep = calculateDepth((float(p)), cast.Latitude)
                    Dictionary[i].append(dep)
            except Exception as e:
                print(e.__str__())
                continue

    for column in Dictionary:
        try:
            df[column] = Dictionary[column]
        except:
            df[column] = np.nan
    return df

###########################################################################################################

 # Save changes of original datafile as new datafile, (new changed file will be called the same as the original but with specified extension '.old' by default)
def cnv_write(cast, df, ext=".old"):
    """
    Save changes of original datafile as new datafile, (new changed file will be called the same as the original but with specified extension '.old' by default)

    :param cast: Cast Object (already populated)
    :param df: Cast Dataframe
    :param ext: filetype extension (String, ie: '.txt', '.old', '.new', ect...)
    :return:
    """
    newfile = cast.datafile + ext
    writer = open(newfile, "w+")
    for l in cast.software:
        writer.write(l + "\n")
    for l in cast.userInput:
        writer.write(l + "\n")
    for l in cast.InstrumentInfo:
        writer.write(l + "\n")
    writer.write("*END*\n")
    writer.write(df.to_string(header=False, index=False))

###########################################################################################################

 # Create a simple text file from datafile (new changed file will be called the same as the original but with specified extension '.simple' by default)
def cnv_write_simple(cast, df, ext=".simple"):
    """
    Create a simple text file from datafile (new changed file will be called the same as the original but with specified extension '.simple' by default)

    :param cast: Cast Object (already populated)
    :param df: Cast Dataframe
    :param ext: filetype extension (String, ie: '.txt', '.old', '.new', ect...)
    :return:
    """
    newfile = cast.datafile + ext
    writer = open(newfile, "w+")
    for l in cast.userInput:
        writer.write(l.replace("**", "") + "\n")

    writer.write("END\n")
    writer.write(df.to_string(header=True, index=False))

###########################################################################################################


def cnv_igoss(cast, df):
    # output data to file
    """
    fille name is based on ship and trip followed by _IGOSS.DTA
    *******************************************************************
    Header portion:
    *******************************************************************

    KKYY DAYMONTHYEAR HOUR|MIN Q|LAT(DEGMIN) LON 888|K1|K2 manufactType
    K1:
    7 - selected depths
    8 - significant depths
    K2:
    0 - No salinity reading
    1 - 1 in situ sensor better than 0.02 PSU
    2 - 1 in situ sensor less than 0.02 PSU
    3 - sample analysis
    q (Quadrant)	Latitude	Longitude
    1	            North	    East
    3	            South	    East
    5	            South   	West
    7	            North   	West

    manufactType
    if its a CTD cast, we use code 83099
    The first three number give the type (830 is a CTD), in this case, 099 means unidentified and Dave seems to
    use that for every CTD, so a CTD igoss will always use 83099
    now, the first three numbers change if its an XBT,

    an XBT-05 uses 011
    XBT-06 uses 032
    XBT-10 uses 061
    XBT-07 uses 042

    it appears that the second two numbers on an XBT is always "06" as opposed to the CTD using "99"

    *******************************************************************
    Data portion:
    *******************************************************************
    2|depth 3|temp 4|salinity 55555=(section indicator for depth) 1|MaxDepth
    """
    """
    :param cast: Cast Object
    :param df: Cast Dataframe
    :return:
    """

    # Create dataframe specific to IGOSS
    df = cnv_sig_dataframe(cast)

    def normalizeLength(str):
        str = str.replace(".", "")
        nstr = ""
        if str.__len__() == 4:
            return str
        elif str.__len__() == 3:
            nstr = "0" + str
        elif str.__len__() == 2:
            nstr = "00" + str
        elif str.__len__() == 1:
            nstr = "000" + str
        else:
            print("NORMALIZE ERROR: " + str)
            nstr = "0000"
        return nstr
    def calculateQuadrant(cast):
        # True is positive coord false is negative
        latpos = True
        lonpos = True
        if cast.Latitude.__str__().__contains__('-'):
            latpos = False
        if cast.Longitude.__str__().__contains__('-'):
            lonpos = False
        if latpos and lonpos:
            return "1"
        elif latpos and not lonpos:
            return "7"
        elif not latpos and lonpos:
            return "3"
        elif not latpos and not lonpos:
            return "5"
    outfile = cast.ship.__str__() + cast.trip.__str__() + "_IGOSS.DTA"
    writer = open(outfile, "a+")
    date = cast.CastDatetime.replace("-", " ").split(" ")
    dmy = "KKYY " + date[2] + date[1] + date[0][-2:]
    hm = date[3].split(":")
    hourmin = hm[0] + hm[1]
    q = calculateQuadrant(cast)
    templat = cast.Latitude.__str__().split(".")
    templon = cast.Longitude.__str__().split(".")
    lat_to_deg_min = templat[0].__str__() + (float(templat[1]) * 60).__str__()
    lon_to_deg_min = templon[0] + (float(templon[1]) * 60).__str__()
    # dropping any '-' because sign denoted by quadrant
    qlat_lon = q + lat_to_deg_min.replace("-", "")[:5] + " " + lon_to_deg_min.replace("-", "")[:5]
    k1 = cast.k1  # TODO: check values for k1 always assuming significant depths
    if not cast.isSalinity:
        cast.k2 = "0"
    k2 = cast.k2
    info = "888" + k1 + k2
    inst = ""
    isXBT = False
    if not cast.Instrument == "":
        if cast.Instrument.upper().__contains__("XBT") and cast.Instrument.upper().__contains__("05"):
            inst = "011"
            isXBT = True
        elif cast.Instrument.upper().__contains__("XBT") and cast.Instrument.upper().__contains__("06"):
            inst = "032"
            isXBT = True
        elif cast.Instrument.upper().__contains__("XBT") and cast.Instrument.upper().__contains__("07"):
            inst = "042"
            isXBT = True
        elif cast.Instrument.upper().__contains__("XBT") and cast.Instrument.upper().__contains__("10"):
            inst = "061"
            isXBT = True
        else:
            # Not XBT then it is a CTD
            inst = "830"

    if isXBT:
        # XBT ends with 06
        header = dmy + " " + hourmin + " " + qlat_lon + " " + info + inst + "06" + "\n"
    else:
        # CTD ends with 99
        header = dmy + " " + hourmin + " " + qlat_lon + " " + info + inst + "99" + "\n"


    writer.writelines(header)
    # dep tmp sal
    # depth whole num
    count = 0
    localdep = 0
    localtmp = 0
    localsal = 0
    if cast.isPressure and cast.isTemperature and cast.isSalinity:
        for i in range(df.shape[0]):
            localdep = int(df["Depth"][i].round()).__str__()
            localsal = df["Salinity"][i].round(2).__str__()
            if df.values[i][1] < 0:
                localtmp = (abs(df["Temperature"][i]) + 50).round(2).__str__()
            else:
                localtmp = df["Temperature"][i].round(2).__str__()
            localdep = normalizeLength(localdep)
            localtmp = normalizeLength(localtmp)
            localsal = normalizeLength(localsal)
            if count == 3:
                line = "2" + localdep + " " + "3" + localtmp + " " + "4" + localsal + "\n"
                count = 0
            else:
                line = "2" + localdep + " " + "3" + localtmp + " " + "4" + localsal + " "
                count = count + 1
            writer.writelines(line)
    elif cast.isPressure and cast.isTemperature and not cast.isSalinity:
        for i in range(df.shape[0]):
            localdep = int(df["Depth"][i].round()).__str__()
            if df.values[i][1] < 0:
                localtmp = (abs(df["Temperature"][i]) + 50).round(2).__str__()
            else:
                localtmp = df["Temperature"][i].round(2).__str__()
            localdep = normalizeLength(localdep)
            localtmp = normalizeLength(localtmp)
            if count == 3:
                line = "2" + localdep + " " + "3" + localtmp + "\n"
                count = 0
            else:
                line = "2" + localdep + " " + "3" + localtmp + " "
                count = count + 1
            writer.writelines(line)
    writer.writelines("." + cast.ShipName + "\n")

###########################################################################################################
# DF considers only the downcast, used for igoss writer
def cnv_sig_dataframe(cast):
    """
     Creates DF for IGOSS writer. DF considers only the downcast, used for igoss writer
     Assigns significant points from the datafile by using a bin smoothing technique.

    :param cast: Cast Object (already populated)
    :return: dataframe to be used with igoss writer
    """
    cast.isPressure = False
    cast.isTemperature = False
    cast.isSalinity = False
    cast.hasDepth = False

    pressureIndex = 0
    temperatureIndex = 0
    salinityIndex = 0

    depthArray = []
    temperatureArray = []
    salinityArray = []

    # loop through Instrument array to dynamically get the indexes for each data column.
    for row in cast.InstrumentInfo:
        if row.lower().__contains__("pressure") and not cast.isPressure:
            cast.isPressure = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
        elif row.lower().__contains__("depth") and not cast.isPressure:
            cast.isPressure = True
            cast.hasDepth = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])

        elif row.lower().__contains__("temperature") and not cast.isTemperature:
            cast.isTemperature = True
            sRow = row.split(" ")
            temperatureIndex = int(sRow[2])

        elif row.lower().__contains__("salinity") and not cast.isSalinity:
            cast.isSalinity = True
            sRow = row.split(" ")
            salinityIndex = int(sRow[2])

    # sorting the data into salinity, temperature and depth
    lastDepth = -1
    for data in cast.data:
        if cast.hasDepth:
            depth = float(data[pressureIndex])
        else:
            # Note: here we are converting pressure to depth
            depth = calculateDepth(float(data[pressureIndex]), cast.Latitude)

        # Take downcast only.
        if depth - lastDepth > 0:
            depthArray.append(depth)
            if cast.isTemperature:
                temperatureArray.append(float(data[temperatureIndex]))
            if cast.isSalinity:
                salinityArray.append(float(data[salinityIndex]))
            lastDepth = depth
        else:
            # Continue instead of break in case of error/bobbing with readings.
            continue

    temp = list(zip(depthArray, temperatureArray, salinityArray))
    sigData = []

    # Get sig points
    for index in range(temperatureArray.__len__()):
        sigData.append(False)

    # Setting first and last points true
    sigData[0] = True
    sigData[temperatureArray.__len__() - 1] = True

    # TODO change method to return inflection points.
    def binSmoothing(depthArray, temperatureArray):
        Bin = []
        depthIndex = []
        sigIndex = []
        numBins = math.ceil(math.sqrt(temperatureArray.__len__()))
        width = math.ceil(temperatureArray.__len__() / numBins)

        count = 0
        index = 0
        row = []
        for t in temperatureArray:
            if count < width:
                row.append(t)
                count = count + 1
                index = index + 1
            else:
                sum = 0
                for r in row:
                    sum = sum + r
                avg = sum / row.__len__()
                Bin.append(avg)
                depthIndex.append(depthArray[index])
                sigIndex.append(index)
                count = 0

        return sigIndex

    # return an array containing the significant indexes.
    sig = binSmoothing(depthArray, temperatureArray)
    ntem = []
    ndep = []
    nsal = []
    for s in sig:
        if cast.isTemperature:
            ntem.append(temperatureArray[s])
        if cast.isPressure:
            ndep.append(depthArray[s])
        if cast.isSalinity:
            nsal.append(salinityArray[s])

    df = pd.DataFrame()
    if cast.isPressure:
        df['Depth'] = ndep
    if cast.isTemperature:
        df['Temperature'] = ntem
    if cast.isSalinity:
        df['Salinity'] = nsal

    return df

###########################################################################################################
def getCastType(cast):
    """
    Assigns cast type variable to cast object V - Vertical or T - Tow
    :param cast: Cast Object (already populated)
    :return:
    """
    if cast.castType == "":
        for i in cast.InstrumentInfo:
            if i.lower().__contains__("nquan"):
                nquan = int(i.split("=")[1].lstrip().rstrip())
                # less than 3 data columns is XBT (Vertical)
                if nquan <= 3:
                    cast.castType = "V"
                    return
                # Greater than 8 is Vertical
                elif nquan >= 8:
                    cast.castType = "V"
                    return
                # Else assume tow
                else:
                    cast.castType = "T"
                    return
###########################################################################################################

# Fetches cast data from Database
def FetchCastObject(cast, conn):

    c = conn.cursor()

    # writeAll = input("Fetch All Files? [1] Yes / [2] No\n")
    writeAll = 1

    # Select All data from Casts.
    if int(writeAll) == 1:
        c.execute("SELECT * FROM Casts")

    # Select only one cast.
    else:
        selectedID = input("Enter Cast ID: ")
        c.execute("SELECT * FROM Casts Where id = '{castID}'".format(castID=selectedID))

    rows = c.fetchall()
    # Create Cast instance for each querry.
    for row in rows:
        cast.id = row[0]
        cast.ShipName = row[1]
        cast.ship = row[2]
        cast.trip = row[3]
        cast.station = row[4]
        cast.Latitude = row[5]
        cast.Longitude = row[6]
        cast.SounderDepth = row[7]
        cast.Instrument = row[8]
        cast.InstrumentName = row[9]
        cast.comment = row[10]
        cast.NumScans = row[11]
        cast.SamplingRate = row[12]
        cast.ChannelCount = row[13]
        cast.DataChannels = row[14]
        cast.MinDepth = row[15]
        cast.MaxDepth = row[16]
        cast.CastDatetime = row[17]
        cast.File = row[18]
        cast.Language = row[19]
        cast.Encoding = row[20]
        cast.Contact = row[21]
        cast.Country = row[22]
        cast.MaintenanceContact = row[23]
        cast.OrgName = row[24]
        cast.DataLimit = row[25]

###########################################################################################################

# Creates dataframe using midlayer variables as the columns in order to standardize the column names
def StandardizedDF(cast, df):
    """
    Creates dataframe using midlayer variables as the columns in order to standardize the column names

    :param cast: Cast Object (already populated)
    :param df: Cast Dataframe
    :return: Dataframe containing standardised names
    """

    col = df.columns._values
    newdf = pd.DataFrame()
    oldName = ""
    newName = ""
    cast.ColumnNames = []
    qa = False

    # for c in cast.ColumnNames:
    for c in col:
        qa = True
        name = c.replace("/", "+")
        if c.lower().__eq__('prdm'):
            newdf['Pressure'] = df[c].values
            oldName = c
            newName = 'Pressure'

        elif c.lower().__eq__('Pressure'):
            newdf['Pressure'] = df[c].values
            oldName = c
            newName = 'Pressure'

        elif c.lower().__eq__('t090c'):
            newdf['Temperature'] = df[c].values
            oldName = c
            newName = 'Temperature'

        elif c.lower().__eq__('t190c'):
            newdf['Secondary Temperature'] = df[c].values
            oldName = c
            newName = 'Secondary Temperature'

        elif c.lower().__eq__('Temperature'):
            newdf['Temperature'] = df[c].values
            oldName = c
            newName = 'Temperature'

        elif c.lower().__eq__('c0s/m'):
            newdf['Conductivity'] = df[c].values
            oldName = c
            newName = 'Conductivity'

        elif c.lower().__eq__('c1s/m'):
            newdf['Secondary Conductivity'] = df[c].values
            oldName = c
            newName = 'Secondary Conductivity'

        elif c.lower().__eq__('cond'):
            newdf['Conductivity'] = df[c].values
            oldName = c
            newName = 'Conductivity'

        elif c.lower().__eq__('cstarat0'):
            newdf['Transmissometer attenuation'] = df[c].values
            oldName = c
            newName = 'Transmissometer attenuation'

        elif c.lower().__eq__('tra'):
            newdf['Transmissometer attenuation'] = df[c].values
            oldName = c
            newName = 'Transmissometer attenuation'

        elif c.lower().__eq__('tranmissometer attenuation'):
            newdf['Transmissometer attenuation'] = df[c].values
            oldName = c
            newName = 'Transmissometer attenuation'

        elif c.lower().__eq__('cstartr0'):
            newdf['Transmissometer transmission'] = df[c].values
            oldName = c
            newName = 'Transmissometer transmission'

        elif c.lower().__eq__('trp'):
            newdf['Transmissometer transmission'] = df[c].values
            oldName = c
            newName = 'Transmissometer transmission'

        elif c.lower().__eq__('tranmissometer transmission'):
            newdf['Transmissometer transmission'] = df[c].values
            oldName = c
            newName = 'Transmissometer transmission'

        elif c.lower().__eq__('depth'):
            newdf['Depth'] = df[c].values
            oldName = c
            newName = 'Depth'

        elif c.lower().__eq__('flag'):
            newdf['Flag'] = df[c].values
            oldName = c
            newName = 'Flag'

        elif c.lower().__eq__('fleco-afl'):
            newdf['Chlorophyll A Fluorescence'] = df[c].values
            oldName = c
            newName = 'Chlorophyll A Fluorescence'

        elif c.lower().__eq__('flor'):
            newdf['Fluorescence'] = df[c].values
            oldName = c
            newName = 'Fluorescence'

        elif c.lower().__eq__('oxsatml/l'):
            newdf['Oxygen Saturation'] = df[c].values
            oldName = c
            newName = 'Oxygen Saturation'

        elif c.lower().__eq__('oxy'):
            newdf['Oxygen Saturation'] = df[c].values
            oldName = c
            newName = 'Oxygen Saturation'

        elif c.lower().__eq__('par'):
            newdf['Irradiance'] = df[c].values
            oldName = c
            newName = 'Irradiance'

        elif c.lower().__eq__('par/sat/log'):
            newdf['Photosynthetic Active Radiation'] = df[c].values
            oldName = c
            newName = 'Photosynthetic Active Radiation'

        elif c.lower().__eq__('ph'):
            newdf['pH'] = df[c].values
            oldName = c
            newName = 'pH'

        elif c.lower().__eq__('pres'):
            newdf['Pressure'] = df[c].values
            oldName = c
            newName = 'Pressure'

        elif c.lower().__eq__('sal'):
            newdf['Salinity'] = df[c].values
            oldName = c
            newName = 'Salinity'

        elif c.lower().__eq__('Salinity'):
            newdf['Salinity'] = df[c].values
            oldName = c
            newName = 'Salinity'

        elif c.lower().__eq__('sal00'):
            newdf['Salinity'] = df[c].values
            oldName = c
            newName = 'Salinity'

        elif c.lower().__eq__('sal11'):
            newdf['Secondary Salinity'] = df[c].values
            oldName = c
            newName = 'Secondary Salinity'

        elif c.lower().__eq__('sbeox0ml/l'):
            newdf['Oxygen'] = df[c].values
            oldName = c
            newName = 'Oxygen'

        elif c.lower().__eq__('sbeox0v'):
            newdf['Oxygen Raw'] = df[c].values
            oldName = c
            newName = 'Oxygen Raw'

        elif c.lower().__eq__('sbeox1ml/l'):
            newdf['Secondary Oxygen'] = df[c].values
            oldName = c
            newName = 'Secondary Oxygen'

        elif c.lower().__eq__('sbeox1v'):
            newdf['Secondary Oxygen Raw'] = df[c].values
            oldName = c
            newName = 'Secondary Oxygen Raw'

        elif c.lower().__eq__('scan'):
            newdf['scan'] = df[c].values
            qa = False

        elif c.lower().__eq__('sigma-t00'):
            newdf['Density'] = df[c].values
            oldName = c
            newName = 'Density'

        elif c.lower().__eq__('sigma-t11'):
            newdf['Secondary Density'] = df[c].values
            oldName = c
            newName = 'Secondary Density'

        elif c.lower().__eq__('sigt'):
            newdf['Density'] = df[c].values
            oldName = c
            newName = 'Density'

        elif c.lower().__eq__('sigmat'):
            newdf['Density'] = df[c].values
            oldName = c
            newName = 'Density'

        elif c.lower().__eq__('temp'):
            newdf['Temperature'] = df[c].values
            oldName = c
            newName = 'Temperature'

        elif c.lower().__eq__('wetcdom'):
            newdf['CDOM Fluorescence'] = df[c].values
            oldName = c
            newName = 'CDOM Fluorescence'

        elif c.lower().__eq__('wet'):
            newdf['CDOM Fluorescence'] = df[c].values
            oldName = c
            newName = 'CDOM Fluorescence'

        elif c.lower().__eq__('depsm'):
            newdf['Depth'] = df[c].values
            oldName = c
            newName = 'Depth'

        elif c.lower().__eq__('tv290c'):
            newdf['Temperature'] = df[c].values
            oldName = c
            newName = 'Temperature'

        else:
            newdf[c] = df[c].values
            qa = False
            print("UNKNOWN VARIABLE: " + c.__str__())
            newName = c
        if qa:
            QA = "** QA Applied: variable " + oldName + " renamed to " + newName
            cast.userInput.append(QA)
        if not newName.__eq__(""):
            cast.ColumnNames.append(newName)

    return newdf

###########################################################################################################
def createTripTag(cast):
    """
    Appends a Trip Tag to the user input section of the metadata
    :param cast: Cast Object (already populated)
    :return:
    """
    print("Select Tag for: " + cast.filename + "\n[1] AZMP\n[2] MULTISPECIES\n[3] NSRF\n[4] Station27\n[5] Calibration\n[6] Other DFO\n[7] Not Yet Classified\n[8] prompt for user input (last resort)")
    tag = input()

    for line in cast.userInput:
        if line.upper().__contains__("TRIP TAG"):
            cast.userInput.remove(line)

    if tag == "1":
        cast.userInput.append("** TRIP TAG: AZMP")
    elif tag == "2":
        cast.userInput.append("** TRIP TAG: MULTISPECIES")
    elif tag == "3":
        cast.userInput.append("** TRIP TAG: NSRF")
    elif tag == "4":
        cast.userInput.append("** TRIP TAG: Station27")
    elif tag == "5":
        cast.userInput.append("** TRIP TAG: Calibration")
    elif tag == "6":
        cast.userInput.append("** TRIP TAG: Other DFO")
    elif tag == "7":
        cast.userInput.append("** TRIP TAG: Not Yet Classified")
    elif tag == "8":
        print("\nEnter Custom Tag: ")
        custom = input()
        cast.userInput.append("** Trip Tag: " + custom)
    else:
        print("Invalid Tag Number!!")
        return createTripTag(cast)

###########################################################################################################

def NCWrite(cast, df, nc_outfile="NCFile"):
    """
    Takes Cast object and dataframe and creates a NETCDF using a standard naming scheme for the variables
    Variable names are converted to a standard name from cast.ColumnNames which is populated during function call
    df = cnv_tk.cnv_to_dataframe(cast)

    To create and populate needed params:
    cast = cnv_tk.Cast(datafile)        # Creates an empty Cast type object
    cnv_tk.cnv_meta(cast, datafile)     # Populates meta variables and data arrays within the Cast object
    df = cnv_tk.cnv_to_dataframe(cast)  # Creates and returns a pandas dataframe using data from cast

    :param cast: Cast Object (already populated)
    :param df: Cast Dataframe
    :return:
    """
    ####################################################################################################
    # NETCDF CREATION HERE:
    ####################################################################################################
    #nc_outfile = cast.datafile.replace(".cnv", "").replace(".CNV", "") + "BINNED.nc"
    nc_out = nc.Dataset(nc_outfile, 'w', format='NETCDF3_CLASSIC')
    nc_out.Conventions = 'CF-1.6'
    nc_out.title = 'NAFC netCDF file'
    nc_out.institution = 'Northwest Atlantic Fisheries Centre, Fisheries and Oceans Canada'
    #nc_out.source = cast.datafile
    nc_out.references = ''
    #nc_out.description = cast.comment
    nc_out.created = 'Created ' + tt.ctime(tt.time())
    # nc_out.processhistory = history
    #nc_out.trip_id = cast.id
    #nc_out.instrument_type = cast.InstrumentName
    #nc_out.instrument_ID = cast.Instrument
    #nc_out.shipname = cast.ShipName
    #nc_out.nafc_shipcode = cast.ship
    #nc_out.time_of_cast = cast.CastDatetime
    nc_out.format_of_time = "YYYY-MM-DD HH:MM:SS"

    history = []
    # Here we are adding all header info into the history
    for h in cast.header:
        history.append(h.__str__().replace('\n', '').replace('(', '').replace(')', '').replace("'", ''))

    num_history_lines = np.size(history)
    # NOTE: ERROR when trying to exec only with map
    # for i in range(0, num_history_lines):
    # exec ('nc_out.processhistory_' + str(i) + ' = ' + ' \' ' + history[i].replace('\n','') + ' \' ')
    # Create dimensions
    time = nc_out.createDimension('time', None) # changed "1" to "None" so the time dimension is UNLIMITED.
    # level = nc_out.createDimension('level', len(df_temp.columns))
    level = nc_out.createDimension('level', df.shape[0])
    nchar = nc_out.createDimension('nchar', 20)
    #str_dim = nc_out.createDimension('str_dim', 1)
    
    #level = nc_out.createDimension('level', None) #changed from df.shape[0] to None so dimension is unlimited, this is to add in merging multiple NC files afterwards - this failed
    # Create coordinate variables
    times = nc_out.createVariable('time', np.float64, ('time',))
    levels = nc_out.createVariable('level', np.float32, ('level',))
    # **** NOTE: Maybe consider using ID instead of time for dimension **** #
    
    # Create 1D variables
    latitudes = nc_out.createVariable('latitude', np.float32, ('time'), zlib=True)
    longitudes = nc_out.createVariable('longitude', np.float32, ('time'), zlib=True)
    sounder_depths = nc_out.createVariable('sounder_depth', np.float32, ('time'), zlib=True)
    
    
    
    #shipname_var = nc_out.createVariable('ShipName', str, ('time'), zlib=True)
    #NAFC_tripid_var = nc_out.createVariable('trip_ID', str, ('time'), zlib=True)
    #comments = nc_out.createVariable('Comments', str, ('time'), zlib=True)
    #instrument_name_var = nc_out.createVariable('Instrument_type', str, ('time'), zlib=True)
    #instrument_id_var = nc_out.createVariable('Instrument_ID', str, ('time'), zlib=True)
    #datafile_source_var = nc_out.createVariable('Datafile_Source', str, ('time'), zlib=True)
    
    shipname = nc_out.createVariable('shipname', 'S1', ('time','nchar',), zlib=True)
    NAFC_tripid = nc_out.createVariable('trip_ID', 'S1', ('time','nchar',), zlib=True)
    instrument_name = nc_out.createVariable('Instrument_type', 'S1', ('time','nchar',), zlib=True)
    instrument_id = nc_out.createVariable('Instrument_ID', 'S1', ('time','nchar',), zlib=True)
    datafile_source = nc_out.createVariable('Datafile_Source', 'S1', ('time','nchar',), zlib=True)

    Dictionary = {}
    for c in df:
        name = c.replace("/", "+")
        if c.lower().__eq__('prdm') or c.__eq__('Pressure'):
            v = nc_out.createVariable('PRESPR01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "dbar"
            v.long_name = "Sea Water Pressure in dbar"
            Dictionary['Pressure'] = [v, name]

        elif c.lower().__eq__('t090c') or c.__eq__('Temperature'):
            # TEMPS901 	Temperature (ITS-90) of the water body by CTD or STD	CTDTmp90
            v = nc_out.createVariable('TEMPS901', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "degC"
            v.long_name = "Sea Water Temperature"
            Dictionary['Temperature'] = [v, name]

        elif c.lower().__eq__('t190c') or c.__eq__('Secondary Temperature'):
            # TEMPS902	Temperature (ITS-90) of the water body by CTD or STD (second sensor)	CTDTmp90_2
            v = nc_out.createVariable('TEMPS902', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "degC"
            v.long_name = "Sea Water Temperature"
            Dictionary['Secondary Temperature'] = [v, name]

        elif c.lower().__eq__('c0s/m') or c.__eq__('Conductivity'):
            # Electrical conductivity of the water body by CTD
            v = nc_out.createVariable('CNDCST01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "S/m"
            v.long_name = "Sea Water Electrical Conductivity"
            Dictionary['Conductivity'] = [v, name]

        elif c.lower().__eq__('c1s/m') or c.__eq__('Secondary Conductivity'):
            # Electrical conductivity of the water body by CTD (sensor 2)
            v = nc_out.createVariable('CNDCST02', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "S/m"
            v.long_name = "Sea Water Electrical Conductivity"
            Dictionary['Secondary Conductivity'] = [v, name]

        elif c.lower().__eq__('cond'):
            # Electrical conductivity of the water body by CTD
            v = nc_out.createVariable('CNDCST01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "S/m"
            v.long_name = "Sea Water Electrical Conductivity"
            Dictionary['Conductivity'] = [v, name]

        elif c.lower().__eq__('cstarat0') or c.__eq__('Transmissometer attenuation [l per m]') or c.lower().__eq__('transmissometer attenuation'):
            v = nc_out.createVariable('ATTNZS01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "1/m"
            v.long_name = "Attenuation per unit length of the water body by WET Labs transmissometer"
            Dictionary['Transmissometer attenuation [l per m]'] = [v, name]

        elif c.lower().__eq__('cstartr0') or c.__eq__('Transmissometer transmission [%]') or c.lower().__eq__('transmissometer transmission'):
            v = nc_out.createVariable('POPTDR01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "%"
            v.long_name = "Transmittance per 25cm of the water body by WET Labs transmissometer"
            Dictionary['Transmissometer transmission [%]'] = [v, name]

        elif c.lower().__eq__('depth') or c.__eq__('Depth'):
            v = nc_out.createVariable('depth', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "m"
            v.long_name = "Depth in meters"
            Dictionary['Depth'] = [v, name]

        elif c.lower().__eq__('flag'):
            Dictionary['Flag'] = [nc_out.createVariable('Flag', np.float32, ('time', 'level'), zlib=True, fill_value=-9999),
                                  name]

        elif c.lower().__eq__('fleco-afl') or c.__eq__('Chlorophyll A Fluorescence'):
            Dictionary['Chlorophyll A Fluorescence'] = [
                nc_out.createVariable('Chlorophyll A Fluorescence', np.float32, ('time', 'level'), zlib=True, fill_value=-9999),
                name]

        elif c.lower().__eq__('flor') or c.__eq__('Fluorescence'):
            Dictionary['Fluorescence'] = [
                nc_out.createVariable('Fluorescence', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('oxsatml/l') or c.__eq__('Oxygen Saturation'):
            # Saturation of oxygen {O2 CAS 7782-44-7} in the water body [dissolved plus reactive particulate phase]
            v = nc_out.createVariable('OXYSZZ01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "ml/l"
            v.long_name = "Saturation of oxygen"
            Dictionary['Oxygen Saturation'] = [v, name]

        elif c.lower().__eq__('oxy'):
            # Saturation of oxygen {O2 CAS 7782-44-7} in the water body [dissolved plus reactive particulate phase]
            v = nc_out.createVariable('OXYSZZ01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "ml/l"
            v.long_name = "Saturation of oxygen"
            Dictionary['Oxygen Saturation'] = [v, name]

        elif c.lower().__eq__('par') or c.__eq__('Irradiance'):
            Dictionary['Irradiance'] = [
                nc_out.createVariable('Irradiance', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('par/sat/log') or c.__eq__('Photosynthetic Active Radiation'):
            Dictionary['Photosynthetic Active Radiation'] = [
                nc_out.createVariable('Photosynthetic Active Radiation', np.float32, ('time', 'level'), zlib=True,
                                      fill_value=-9999), name]

        elif c.lower().__eq__('ph'):
            Dictionary['pH'] = [nc_out.createVariable('pH', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('pres'):
            v = nc_out.createVariable('PRESPR01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "dbar"
            v.long_name = "Sea Water Pressure in dbar"
            Dictionary['Pressure'] = [v, name]

        elif c.lower().__eq__('sal') or c.__eq__('Salinity'):
            # Practical salinity of the water body by CTD and computation using UNESCO 1983 algorithm
            v = nc_out.createVariable('PSALST01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "PSS-78"
            v.long_name = "sea_water_practical_salinity"
            Dictionary['Salinity'] = [v, name]

        elif c.lower().__eq__('sal00'):
            v = nc_out.createVariable('PSALST01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "PSS-78"
            v.long_name = "sea_water_practical_salinity"
            Dictionary['Salinity'] = [v, name]

        elif c.lower().__eq__('sal11') or c.__eq__('Secondary Salinity'):
            # Practical salinity of the water body by CTD (second sensor) and computation using UNESCO 1983 algorithm
            v = nc_out.createVariable('PSALST02', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "PSS-78"
            v.long_name = "sea_water_practical_salinity"
            Dictionary['Secondary Salinity'] = [v, name]

        elif c.lower().__eq__('sbeox0ml/l') or c.__eq__('Oxygen'):
            v = nc_out.createVariable('DOXYZZ01', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "ml/l"
            v.long_name = "Oxygen concentration"
            Dictionary['Oxygen'] = [v, name]

        elif c.lower().__eq__('sbeox0v') or c.__eq__('Oxygen Raw'):
            # Raw signal (voltage) of instrument output by oxygen sensor
            v = nc_out.createVariable('OXYVLTN1', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "V"
            v.long_name = "Raw signal (voltage) of instrument output by in-situ microelectrode"
            Dictionary['Oxygen Raw'] = [v, name]

        elif c.lower().__eq__('sbeox1ml/l') or c.__eq__('Secondary Oxygen'):
            Dictionary['Secondary Oxygen'] = [
                nc_out.createVariable('Secondary Oxygen', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sbeox1v') or c.__eq__('Secondary Oxygen Raw'):
            # Raw signal (voltage) of instrument output by oxygen sensor (second sensor)
            v = nc_out.createVariable('OXYVLTN2', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "V"
            v.long_name = "Raw signal (voltage) of instrument output by in-situ microelectrode (second sensor)"
            Dictionary['Secondary Oxygen Raw'] = [v, name]

        elif c.lower().__eq__('scan'):
            continue
            # Dictionary['Scan'] = [nc_out.createVariable('Scan', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigma-t00') or c.__eq__('Density'):
            Dictionary['Density'] = [
                nc_out.createVariable('Density', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigma-t11') or c.__eq__('Secondary Density'):
            Dictionary['Secondary Density'] = [
                nc_out.createVariable('Secondary Density', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigt'):
            Dictionary['Density'] = [
                nc_out.createVariable('Density', np.float32, ('time', 'level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('temp'):
            # TEMPS901 	Temperature (ITS-90) of the water body by CTD or STD	CTDTmp90
            v = nc_out.createVariable('TEMPS901', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "degC"
            v.long_name = "Sea Water Temperature"
            Dictionary['Temperature'] = [v, name]

        elif c.lower().__eq__('wetcdom') or c.__eq__('CDOM Fluorescence'):
            # Fluorescence of the water body by linear-response CDOM fluorometer
            v = nc_out.createVariable('FLUOCDOM', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "mg/m^3"
            v.long_name = "CDOM Fluorescence"
            Dictionary['CDOM Fluorescence'] = [v, name]

        elif c.lower().__eq__('tv290c'):
            # TEMPS901 	Temperature (ITS-90) of the water body by CTD or STD	CTDTmp90
            v = nc_out.createVariable('TEMPS901', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "degC"
            v.long_name = "Sea Water Temperature"
            Dictionary['Temperature'] = [v, name]

        elif c.lower().__eq__('depth'):
            # TEMPS901 	Temperature (ITS-90) of the water body by CTD or STD	CTDTmp90
            v = nc_out.createVariable('depth', np.float32, ('time', 'level'), zlib=True, fill_value=-9999)
            v.units = "m"
            v.long_name = "Sea Water Depth"
            Dictionary['Depth'] = [v, name]

        else:
            Dictionary[c] = [nc_out.createVariable(name, np.float32, ('time', 'level'), zlib=True, fill_value=-9999),
                             name]
            print("UNKNOWN VARIABLE: " + c.__str__())
            input("HALT...Press Enter To Continue")

    times.units = 'hours since 1900-01-01 00:00:00'
    times.calendar = 'gregorian'

    # temp[:] = df["temp"].values
    for d in Dictionary:
        index = Dictionary[d][1]
        index = index.replace("+", "/")
        #v = Dictionary[d][0]
        v[0,:] = df[index].values
        Dictionary[d][0][0,:] = df[index].values

    # Fill cast info
    #latitudes[:] = cast.Latitude
    latitudes[:] = cast.Latitude
    longitudes[:] = cast.Longitude
    
    #sounder_depths[:] = str(cast.SounderDepth)
    sounder_depths[:] = str(cast.SounderDepth)
    
    str_out = nc.stringtochar(np.array([cast.ShipName], 'S20'))
    
    shipname[:] = str_out
    
    str_out = nc.stringtochar(np.array([cast.id], 'S20'))
    NAFC_tripid[:] = str_out
    
    str_out = nc.stringtochar(np.array([cast.InstrumentName], 'S20'))
    instrument_name[:] = str_out
    
    str_out = nc.stringtochar(np.array([cast.Instrument], 'S20'))
    instrument_id[:] = str_out
    
    
    str_out = nc.stringtochar(np.array([cast.datafile], 'S20'))
    datafile_source[:] = str_out
    
    
    
    
    # Fill time
    try:
        date = datetime.datetime.strptime(cast.CastDatetime, '%Y-%m-%d %H:%M:%S')
    except:
        cast.CastDatetime = cast.CastDatetime + ":00"
        date = datetime.datetime.strptime(cast.CastDatetime, '%Y-%m-%d %H:%M:%S')
    times[:] = nc.date2num(date, units=times.units, calendar=times.calendar)

    # Typically the pressure/depth index
    pressureIndex = 1
    for row in cast.InstrumentInfo:
        if row.lower().__contains__("pressure") and not cast.isPressure:
            # cast.isPressure = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
        elif row.lower().__contains__("depth") and not cast.isPressure:
            # cast.isPressure = True
            cast.hasDepth = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
    try:
        Pbin = np.array(df['Pressure'], dtype='float64')
    except:
        try:
            Pbin = np.array(df['Depth'], dtype='float64')
        except:
            Pbin = np.array(df[cast.ColumnNames[pressureIndex]], dtype='float64')

    levels[:] = Pbin
    nc_out.close()

###########################################################################################################

def BinDF(cast, df, dropNan=False):
    """
    Creates a Dataframe using a binning technique for datapoint selection
    :param cast:
    :param df:
    :param dropNan:
    :return:
    """
    # Typically the pressure/depth index
    pressureIndex = 0
    """
    for row in cast.InstrumentInfo:
        if row.lower().__contains__("pressure") and not cast.isPressure:
            # cast.isPressure = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
        elif row.lower().__contains__("depth") and not cast.isPressure:
            # cast.isPressure = True
            cast.hasDepth = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
    """
    # Look through df for index relating to pressure
    for col in df:
        if col.lower().__contains__("pressure"):
            break
        elif col.lower().__contains__("depth"):
            break
        pressureIndex = pressureIndex + 1

    df = df.astype(float)
    # df['bin'] = pd.cut(df[cast.ColumnNames[pressureIndex]].astype(float), bins)
    # df = df.dropna(axis='rows')
    print("Binning")

    # Here we are dropping any of the upcast values
    lastdepth = 0
    # array to hold the scans to drop *IMPORTANT: Scans need to be the first column in the dataframe
    toDrop = []
    for d in df.values:
        current = float(d[pressureIndex])
        if float(current) > lastdepth:
            lastdepth = current
        else:
            # Append scans to drop, SCAN MUST BE FIRST COLUMN IN DATAFRAME
            toDrop.append(int(d[0]))

    for s in toDrop:
        i = df.loc[df['scan'].astype(float) == float(s)].index
        index = i.values
        df = df.drop(index[0])

    bins = []
    depths = []
    # Create bin with specified intervals and steps
    for i in range(0, 10001, 1):
        bins.append(i + 0.5)

    """
    #bins.append(1000)
    for i in range(1000, 5000, 10):
        bins.append(i)
    """
    count = 0
    for b in bins:
        depths.append(b + 0.5)

        """
        if count < 1001:
            depths.append(b + 0.5)
            count = count + 1
        else:
            nd = b + 5
            depths.append(nd)
            count = count + 1
        """
    # Store column names into temp list
    tempColumnNames = []
    for c in df:
        tempColumnNames.append(c)

    # Here we bin all the data and calculate the mean for each bin
    df = df.groupby(pd.cut(df[tempColumnNames[pressureIndex]].astype(float), bins)).mean()

    # Had 1 too many values at end
    depths.pop()

    # Create
    # s = df.values.shape[0]
    # newpres = []
    # for s in range(s):
    #    newpres.append(s + 1)

    # Replace mean pressures with bin values
    df[tempColumnNames[pressureIndex]] = depths

    # Drop all empty rows
    if dropNan:
        df = df.dropna(axis=0)

    return df