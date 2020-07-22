import numpy as np
import pandas as pd
import math

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

def calculateDepth(press):

    g = 9.780318

    depth = ((((-1.82*math.pow(10, -15)* press +2.279*math.pow(10,-10))
               *press-2.2512*math.pow(10,-5))
               *press+9.72659)*press)/g

    return depth

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
    isData = False
    for line in f:
        line = line.replace("\n", "")
        if isData:
            cast.data.append(line.replace("\n", "").lstrip().rstrip().split())
        elif line.__contains__("** "):
            cast.userInput.append(line)
            if line.upper().__contains__("VESSEL"):
                if line.__contains__("_"):
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

            elif line.upper() == "LATITUDE" or line.upper() == "LAT":
                line = line.lower().replace("n", "")
                lat = line.split(":")[1].lstrip().rstrip()
                if lat.__len__() >= 5 and not lat.__contains__(" "):
                    x = lat[0:2]
                    y = lat[2:4] + "." + lat[4:]
                    lat = x + " " + y
                cast.Latitude = convertLatLong(lat.split())
            elif line.upper() == "LONGITUDE" or line.upper() == "LON":
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
            elif line.upper() == "SOUNDING":
                cast.SounderDepth = line.split(":")[1]
            elif line.upper() == "COMMENTS":
                cast.comment = line.split(":")[1]
            elif line.upper() == "PROBE":
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
            depth = calculateDepth(float(data[pressureIndex]))

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

    writeAll = input("Write All Files? [1] Yes / [2] No\n")

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

        # Creates a new folder and changes current working directory.
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
                filename = cast.id.__str__() + "_DB.sbe"
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

                read.execute("SELECT Instrument_Info FROM Instrument Where cid like '{castID}'".format(castID=cast.id))
                header = read.fetchall()
                for h in header:
                    f.writelines(h)
                    f.write("\n")

                f.write("*END*\n")
                df.to_string(f)
                f.close()

            else:
                filename = cast.id.__str__() + "_P_DB.sbe"
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

            filename = cast.id.__str__() + "_sbe_DB.p"
            # Creating the file name based on the deployment ID and the deployment date.
            f = open(filename, "w+")

            if cast.File.lower().endswith("sbe"):

                def DecimalDegrees_to_DegreesMins(lat, lon):
                    latDeg = lat[0:2]
                    lonDeg = lon[0:3]
                    latMins = lat[3:5]
                    lonMins = lon[4:5]

                    latMins = float(latMins)*60
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

                    cast.Latitude = latDeg + " " +latMins
                    cast.Longitude = lonDeg + " " +lonMins

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


                f.write(cast.id.__str__() + "  " + cast.Latitude.__str__() + " " + cast.Longitude.__str__().replace("-", "-0") + " " + cast.CastDatetime.__str__() + " " + cast.SounderDepth.__str__() + " " + cast.Instrument.__str__() + " " + cast.setNumber.__str__() + " " + cast.castType.__str__() + " " + cast.comment.__str__())
                f.write("\n-- Data --\n")
                df.to_string(f)
                print("SBE")

            else:
                filename = cast.id.__str__() + "_P_DB.p"
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
            cmt = row[12]
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

                for i in range(0, num_history_lines):
                    exec('nc_out.processhistory_' + str(i) + ' = ' + ' \' ' + history[i].replace('\n', '') + ' \' ')

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



###########################################################################################################