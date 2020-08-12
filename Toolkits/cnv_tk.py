import numpy as np
import pandas as pd
import math
import seawater as sw
"""
Toolkit for creating cast object types from cnv files
cnv_to_dataframe: dynamically creates a pandas dataframe based on the fields within the datafile
cnv_meta: Populates the fields within the Cast object

Required Files:
"CTD Instrument Info.xlsx"
"ships.txt"

Created By: Dylan Kennedy
03-05-2020
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
    x = math.pow(math.sin(latitude/57.29578), 2)
    g = 9.780318*(1*(5.2788*math.pow(10, -3)+2.36*math.pow(10, -5)*x)*x)+1.092*math.pow(10, -6)*press

    depth = ((((-1.82*math.pow(10, -15)* press +2.279*math.pow(10,-10))
               *press-2.2512*math.pow(10,-5))
               *press+9.72659)*press)/g

    return depth
    """
    depth = sw.dpth(107.051, latitude)
    return depth

###########################################################################################################

def calculatePress(depth, latitude):
    """
    x = math.pow(math.sin(latitude / 57.29578), 2)
    partial_g = 9.780318 * (1 * (5.2788 * math.pow(10, -3) + 2.36 * math.pow(10, -5) * x) * x)+1.092*math.pow(10, -6)

    press = ((((-1.82*math.pow(10, -15) +2.279*math.pow(10,-10))
               -2.2512*math.pow(10,-5))
               +9.72659))/(depth*partial_g)

    return press
    """
    press = sw.pres(depth, latitude)
    return press

###########################################################################################################
def cnv_ascii(cast):
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
    f = open(datafile)
    filetype_v2 = False # bool to tell if file uses different format type
    isData = False
    for line in f:
        line = line.replace("\n", "")
        if isData:
            cast.data.append(line.replace("\n", "").lstrip().rstrip().split())
        if line.__contains__("System UpLoad Time"):
            filetype_v2 = True
            tempdate = line.split("=")[1].split()
            convertDate(cast, tempdate)
        elif line.__contains__("** "):
            cast.userInput.append(line)
            if line.upper().__contains__("VESSEL"):
                if filetype_v2:
                    l = line.split(":")[1].lstrip().rstrip().split("_")
                    cast.ship = l[0]
                    cast.trip = l[1]
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
            elif line.upper().__contains__("PROBE"):
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
    getInstrumentName(cast, "CTD Instrument Info.xlsx")

###########################################################################################################

def getInstrumentName(cast, refFile):

    try:
        dfs = pd.read_excel(refFile, sheet_name="Sheet1")
    except:
        dfs = pd.read_excel("../Resources/CTD Instrument Info.xlsx", sheet_name="Sheet1")
    #dfs = pd.read_csv(refFile, sep=" ", header=None)


    for i in dfs.index:
        if cast.Instrument.__contains__(dfs['Serial Number (SN)'][i].__str__()):
            cast.InstrumentName = dfs['Instrument Type (SBE-CTD)'][i]

###########################################################################################################

def getShipName(cast):

    try:
        Ships = open("ships.txt")
    except:
        Ships = open("../Resources/ships.txt")

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

 # Save changes of origional datafile as new datafile, (new changed file will be called the same as the origional but with extension '.new')
def cnv_write(cast, df, ext=".old"):
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

 # Save changes of origional datafile as new datafile, (new changed file will be called the same as the origional but with extension '.new')
def cnv_write_simple(cast, df, ext=".simple"):
    newfile = cast.datafile + ext
    writer = open(newfile, "w+")
    """
    cast = Cast
    writer.write(cast.ShipName + "\n" +
                 cast.ShipName + "\n" +
                 cast.ShipName + "\n" +
                 cast.ShipName + "\n" +
                 cast.ShipName + "\n" +)
    """
    for l in cast.userInput:
        writer.write(l.replace("**", "") + "\n")

    writer.write("END\n")
    writer.write(df.to_string(header=True, index=False))

###########################################################################################################


def cnv_igoss(cast, df):
    # output data to file
    """
    fille name is based on ship and trip followed by _IGOSS.DTA
    header portion:
    KKYY DAYMONTHYEAR HOUR|MIN Q|LAT(DEGMIN) LON 888|K1|K2 ?????
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
    2|depth 3|temp 4|salinity 55555=(section indicator for depth) 1|MaxDepth
    :param cast:
    :param df:
    :return:
    """
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
    k1 = cast.k1  # TODO: check values for k1 and k2
    if not cast.isSalinity:
        cast.k2 = "0"
    k2 = cast.k2
    info = "888" + k1 + k2
    header = dmy + " " + hourmin + " " + qlat_lon + " " + info + "\n"
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
            depth = calculateDepth(float(data[pressureIndex]), cast.latitude)

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

    """
    TODO: Select only significant depths for the arrays 
    calculate current and previous slopes
    if slope threshold is outside range
    then add the data to the revised array
    else check next slope.

    last, current = [depth, temp, slope]

    slope     = ( y2 - y1 ) / ( x2 - x1 )
    intercept = y1 - (slope) * x1 
    """
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
