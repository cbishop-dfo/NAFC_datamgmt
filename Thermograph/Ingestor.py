import sys
import os
import platform
import glob
import sqlite3
import time
import datetime
import json

__author__ = 'KennedyDyl'


class Deployments(object):

    def __init__(self, datafile=None):
        self.datafile = datafile
        self.initialize_vars()

    def initialize_vars(self):
        self.id = "null"
        self.InstrumentType = "null"
        self.SiteName = "null"
        self.SiteCode = "null"
        self.InstrumentNum = "null"
        self.Latitude = "null"
        self.Longitude = "null"
        self.DeploymentDepth = "null"
        self.DeploymentDate = "null"
        self.DeploymentTime = "null"
        self.RecoveredDate = "null"
        self.TimeOfRecovery = "null"
        self.SamplingSize = "null"
        self.DeploymentSiteDepth = "null"
        self.data = []
        self.directory = DatabaseFile  # DB Location.
        self.datafile = ""
        # Using last modified date as creation date (files seem to have moved around a lot)
        self.creationDate = getCreationDate(datafile)


###########################################################################################################


# Checks to see if identical Location and meta fields already exist in the database
def isMeta(data):
    meta = Deployments()
    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    metadata = conn.cursor()
    metadata.execute("SELECT * FROM Deployments")
    rows = metadata.fetchall()
    metareturn = 'false'
    locationreturn = 'false'

    for row in rows:
        meta.id = row[0]
        meta.InstrumentType = row[1]
        meta.SiteName = row[3]
        meta.SiteCode = row[4]
        meta.InstrumentNum = row[2]
        meta.Latitude = row[5]
        meta.Longitude = row[6]
        meta.DeploymentDate = row[7]
        meta.DeploymentTime = row[8]
        meta.RecoveredDate = row[9]
        meta.TimeOfRecovery = row[10]
        meta.SamplingSize = row[13]
        meta.DeploymentSiteDepth = row[12]
        meta.DeploymentDepth = row[11]

        # Location fields need to be first in list
        fields = ["SiteName", "SiteCode", "Latitude", "Longitude", "DeploymentSiteDepth", "InstrumentNum",
                  "InstrumentType", "DeploymentDepth", "DeploymentDate",
                  "DeploymentTime", "RecoveredDate", "TimeOfRecovery", "SamplingSize"]

        # counters for number of matches of same fields
        sameFields = 0
        sameLocation = 0

        for field in fields:
            if getattr(meta, field) == getattr(data, field):
                sameFields = sameFields + 1
                sameLocation = sameLocation + 1

            # At least one field is different, no need so compare the others
            else:
                break
        # Not considering deployment site depth therefore 4 not 5
        if sameLocation >= 4:
            # Same, identical Location does exist in the database
            locationreturn = 'true'

            if sameFields == fields.__len__():
                # Same, identical meta data does exist in the database
                metareturn = 'true'
                return [metareturn, locationreturn]

    return [metareturn, locationreturn]


def getCreationDate(datafile):  # Getting creation date of the datafile.

    if platform.system() == "Windows":
        # getting last modified date (mtime) seemed more accurate as the files have been moved and copied a lot
        return time.ctime(os.path.getmtime(datafile))
    else:
        stat = os.stat(datafile)
        try:
            return time.ctime(stat.st_birthtime)
        except AttributeError:
            # Assuming Linux, No real way to get creation date. Getting last modified date instead.
            return time.ctime(stat.st_mtime)


def getFilename(datafile):
    path = datafile.replace("\\", "/").split("/")
    return path[path.__len__() - 1]


# Strips away all strings that contain numbers, was getting a lot of dates in site name.
def removeDigit(namelist):
    name = ""
    for dig in namelist:
        namepeice = ""
        validstring = 'true'

        for d in dig:
            namepeice = namepeice + d
            if d.replace("\n", "").isdigit():
                validstring = 'false'
                break

        if validstring == 'true':
            name = name + namepeice + " "

    return name.rstrip()


# Convert Lat / Long into decimals
def convertLatLong(convert):
    if convert.__len__() == 2:
        value = float(convert[0]) + float(convert[1]) / 60
        value = float("{0:.2f}".format(value))
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


# Fixing site locations which contain dates.
def checklocation(name):
    sitename = ""

    if name.__len__() > 1:

        if name[name.__len__() - 1].lower().__contains__("metres"):
            name.__delitem__(name.__len__() - 1)

        if name[name.__len__() - 1].lower().__contains__("jan"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("feb"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("mar"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("apr"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("may"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("jun"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("jul"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("aug"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("oct"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("nov"):
            name.__delitem__(name.__len__() - 1)

        elif name[name.__len__() - 1].lower().__contains__("dec"):
            name.__delitem__(name.__len__() - 1)

    length = 0

    for i in name:  # Combines name list after dates removed
        length = length + 1
        if length < name.__len__():
            sitename = sitename + i + " "
        else:
            sitename = sitename + i
    return sitename.replace("'", "").replace(",", "")


###########################################################################################################


def read_mini_one(datafile):
    print("Pushing " + datafile + " To Database")
    data = Deployments(datafile)
    data.datafile = getFilename(datafile)

    try:
        f = open(datafile, "r")
    except:
        exit()

    def formatDate(date):  # checks that date is yyyy-mm-dd
        temp = date.split("-")
        if len(temp[0]) < 3:
            newdate = temp[2] + "-" + temp[1] + "-" + temp[0]
            return newdate
        else:
            newdate = temp[0] + "-" + temp[1] + "-" + temp[2]
            return newdate

    for line in f:

        if line.replace("\n", "").__eq__(""):
            continue
        else:

            if line.__contains__("Serial"):
                data.InstrumentNum = line.split("=")[1].replace("\n", "")

            elif line.__contains__("Study"):

                # Was having a lot of problems with the site names containing dates and depths.
                study = line.replace("'", "").split("=")[1].split(" ")
                name = removeDigit(study).rstrip()
                data.SiteName = checklocation(name.split(" "))

            elif line.__contains__("Start"):

                # Start and end dates
                timeS = line.split("=")[1].replace(",", " ").split(" ")  # line for start date info
                data.DeploymentTime = timeS[1].replace("\n", "")
                # check to see if date is before 2000
                if timeS[0].startswith("9"):
                    data.DeploymentDate = "19" + timeS[0]
                else:
                    data.DeploymentDate = timeS[0]

            elif line.__contains__("Finish"):

                timeF = line.split("=")[1].replace(",", " ").split(" ")  # line for end date info
                data.TimeOfRecovery = timeF[1].replace("\n", "")
                # check to see if date is before 2000, more specifically in the 90's
                if timeF[0].startswith("9"):
                    data.RecoveredDate = "19" + timeF[0]
                else:
                    # past 2000, date contains all 4 digits for the year
                    data.RecoveredDate = timeF[0]

            elif line.__contains__("Sample"):
                data.SamplingSize = line.split("=")[1].replace("\n", "")

            elif line.__contains__("ID"):
                data.InstrumentType = line.split("=")[1].replace("\n", "")

            elif line.__contains__("yyyy-mm-dd"):
                break

    # f.readline()

    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Checks if identical data exists in database.
    checkMeta = isMeta(data)

    if checkMeta[0] == 'false':
        # Deployment Table
        c.execute("INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                  " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                  " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                  " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}', '{df}')" \
                  .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                          sn=data.SiteName, itp=data.InstrumentType, lat=data.Latitude, long=data.Longitude,
                          dpd=data.DeploymentDepth, datd=data.DeploymentDate, datt=data.DeploymentTime,
                          recd=data.RecoveredDate, rect=data.TimeOfRecovery, ss=data.SamplingSize,
                          sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

        data.id = c.lastrowid

        for lin in f:
            if lin.replace("\n", "").__eq__(""):
                continue
            else:
                l = lin.replace(",", " ").split(" ")
                data.data.append(l)
                dataTime = l[1]
                dataDate = l[0]
                dataTemp = l[2].replace("\n", "")
                # Data Table
                c.execute(
                    "INSERT INTO {tn} ('d_id', 'deployment_id','{tc}', '{yc}', '{tic}' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                        .format(tn='Data', tic='Time', tc='Temperature', fn=data.id,
                                tv=dataTemp,
                                tm=dataTime,
                                yr=dataDate,
                                yc='Year'))

            conn.commit()

    # Location Table
    if checkMeta[1] == 'false':
        c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                  " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                  " '{sd}')" \
                  .format(thn='Location', sc=data.SiteCode,
                          sn=data.SiteName.replace("'", ""),
                          lat=data.Latitude, long=data.Longitude,
                          sd=data.DeploymentSiteDepth))

        conn.commit()

    conn.close()  # Closing connection to the DB.


###########################################################################################################


def read_mini_two(datafile):
    print("Pushing " + datafile + " To Database")
    data = Deployments(datafile)
    data.datafile = getFilename(datafile)

    try:
        f = open(datafile, "r")
    except:
        exit()

    # Some csv files contain source file path inside of the file and use ":" instead of "="
    temp = f.readline()
    if temp.lower().__contains__("source"):
        instrumentline = f.readline()
        # Serial number is on the same line as the instrument type
        serial = instrumentline.split("-")
        for getSerial in serial:
            # Looking for first digit in line, and assuming it's the serial number
            if getSerial.replace("\n", "").isdigit():
                data.InstrumentNum = getSerial.replace("\n", "")
                break

        # removing serial number from line so only inst type remains
        data.InstrumentType = removeDigit(instrumentline.split(":")[1].split("-")).lstrip().replace(" ", "-")
        namelist = f.readline().split(":")[1].split(" ")
        name = removeDigit(namelist)
        data.SiteName = name
        f.readline()

        # Start and end dates
        deploymentDate = f.readline().split(" ")
        data.DeploymentDate = deploymentDate[3]
        data.DeploymentTime = deploymentDate[4].replace("\n", "")
        recoveryDate = f.readline().split(" ")
        data.RecoveredDate = recoveryDate[3]
        data.TimeOfRecovery = recoveryDate[4].replace("\n", "")

        data.SamplingSize = f.readline().split(" ")[2].replace("\n", "")
        f.readline()
    else:
        data.InstrumentType = temp.split("=")[1].replace("\n", "")
        data.InstrumentNum = f.readline().split("=")[1].replace("\n", "")
        namelist = f.readline().split("=")[1].split(" ")
        name = removeDigit(namelist)
        data.SiteName = checklocation(name.split(" "))
        start = f.readline().split("=")[1].split(" ")
        data.DeploymentDate = start[0]
        data.DeploymentTime = start[1].replace("\n", "")
        finish = f.readline().split("=")[1].split(" ")
        data.RecoveredDate = finish[0]
        data.TimeOfRecovery = finish[1].replace("\n", "")
        data.SamplingSize = f.readline().split("=")[1].replace("\n", "")
        f.readline()

    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Checks if identical data exists in database.
    checkMeta = isMeta(data)

    # If data doesn't already exist we can push to the database
    if checkMeta[0] == 'false':
        # Deployment Table
        c.execute("INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                  " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                  " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                  " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}', '{df}')" \
                  .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                          sn=data.SiteName, itp=data.InstrumentType, lat=data.Latitude, long=data.Longitude,
                          dpd=data.DeploymentDepth, datd=data.DeploymentDate, datt=data.DeploymentTime,
                          recd=data.RecoveredDate, rect=data.TimeOfRecovery, ss=data.SamplingSize,
                          sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

        data.id = c.lastrowid

        for lin in f:
            l = lin.split(",")
            data.data.append(l)
            dataTime = l[1]
            dataDate = l[0]
            dataTemp = l[2].replace("\n", "")

            # Data table
            c.execute(
                "INSERT INTO {tn} ('d_id', 'deployment_id','{tc}', '{yc}', '{tic}' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                    .format(tn='Data', tic='Time', tc='Temperature', fn=data.id,
                            tv=dataTemp,
                            tm=dataTime,
                            yr=dataDate,
                            yc='Year'))

        conn.commit()

    # Location Table
    if checkMeta[1] == 'false':
        c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                  " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                  " '{sd}')" \
                  .format(thn='Location', sc=data.SiteCode,
                          sn=data.SiteName.replace("'", ""),
                          lat=data.Latitude, long=data.Longitude,
                          sd=data.DeploymentSiteDepth))
        conn.commit()

    conn.close()  # Closing connection to the DB.


###########################################################################################################


def read_pro(datafile):
    print("Pushing " + datafile + " To Database")

    data = Deployments(datafile)
    data.datafile = getFilename(datafile)

    try:
        f = open(datafile, "r")
    except:
        exit()

    data.SiteName = f.readline().strip().replace(",", "").replace("'", "")
    line = f.readline().split()
    if line.__len__() == 0:
        line = f.readline().split()
    # Some files have missing fields in the meta line, inserting missing fields as "null"
    if line[0].isdigit():
        line.insert(0, "null")  # data missing Instrument Type
        line.insert(10, "null")  # data missing Sampling Size
        line.insert(11, "null")  # data missing Deployment Depth

    elif line[0] == 'H':
        data.InstrumentType = "Hugrun"

    elif line[0] == 'T':
        data.InstrumentType = "Minilog"

    elif line[0] == 'R':
        data.InstrumentType = "Ryan TempMentor"

    else:
        # NOTE: Double check all valid characters. assuming if not H,T,R then SEAMON UTR-B
        data.InstrumentType = "SEAMON UTR-B"

    def convertDate(line):  # Changes day of year to yyyy-mm-dd.
        dateY = line[:2]
        dateDay = line[-3:]
        # some of the pro files we're just before 2000 and they only contain the last two digits of the year
        # checking if any files were before the 80's, there shouldn't be any before the 90's but just being cautious
        if int(dateY) > 80:
            dateF = "19" + dateY + " " + dateDay

        else:
            dateF = "20" + dateY + " " + dateDay

        newDate = datetime.datetime.strptime(dateF, '%Y %j').__str__().split()[0]
        return newDate

    data.SiteCode = line[1]
    data.InstrumentNum = line[2]
    data.Latitude = line[3]
    # West Bias Should actually be negative (don't want to change in case non biased data comes in)
    data.Longitude = line[4]
    data.DeploymentDepth = line[5]
    # To be converted into YYYY-MM-DD.
    data.DeploymentDate = convertDate(line[6])
    data.DeploymentTime = line[7][:2] + ":" + line[7][2:] + ":00"
    # To be converted into YYYY-MM-DD.
    data.RecoveredDate = convertDate(line[8])
    data.TimeOfRecovery = line[9][:2] + ":" + line[9][2:] + ":00"
    data.SamplingSize = line[10]
    data.DeploymentSiteDepth = line[11]

    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Checks if identical data exists in database.
    checkMeta = isMeta(data)

    if checkMeta[0] == 'false':
        # Deployment Table
        c.execute("INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                  " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                  " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                  " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}', '{df}')" \
                  .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                          sn=data.SiteName, itp=data.InstrumentType, lat=data.Latitude, long=data.Longitude,
                          dpd=data.DeploymentDepth, datd=data.DeploymentDate, datt=data.DeploymentTime,
                          recd=data.RecoveredDate, rect=data.TimeOfRecovery, ss=data.SamplingSize,
                          sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

        data.id = c.lastrowid

        f.readline()
        for lin in f:
            l = lin.replace("\n", "").split()
            if l.__len__() == 0:
                continue
            # Some data has escape codes at the end of the datafile
            if l[0].isdigit():
                data.data.append(l)
            else:
                break
            # Data Table
            c.execute(
                "INSERT INTO {tn} ('d_id', 'deployment_id','{tc}', '{yc}', '{tic}' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                    .format(tn='Data', tic='Time', tc='Temperature', fn=data.id,
                            tv=data.data[data.data.__len__() - 1][2].__str__().replace("+", "").replace("-.", "-0."),
                            tm=data.data[data.data.__len__() - 1][1][:2] + ":" + data.data[data.data.__len__() - 1][1][
                                                                                 2:] + ":00",
                            yr=convertDate(data.data[data.data.__len__() - 1][0]),
                            yc='Year'))

        conn.commit()  # Commit changes to the DB.

    # Location Table
    if checkMeta[1] == 'false':
        c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                  " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                  " '{sd}')" \
                  .format(thn='Location', sc=data.SiteCode,
                          sn=data.SiteName.replace("'", ""),
                          lat=data.Latitude, long=data.Longitude,
                          sd=data.DeploymentSiteDepth))
        conn.commit()

    conn.close()  # Closing connection to the DB.c


###########################################################################################################


def read_hugrun(datafile):
    print("Pushing " + datafile + " To Database")
    mini = ""
    data = Deployments(datafile)
    data.datafile = getFilename(datafile)
    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    isDate = True
    isSerial = True
    isSite = True
    headerReady = False
    setStartDate = True

    dat = open(datafile)

    temperatureIndex = 0  # index that will later be used to traverse the data array.

    def formatDate(line):
        old = line.replace("-", "/").split("/")
        new = old[1] + "-" + old[0]
        return new

    count = 0
    for line in dat:
        count = count + 1
        if line.replace("\n", "").__eq__(""):
            continue

        elif isDate:

            lin = line.replace("\n", "").split()
            tempIndex = 0
            temp = []

            for sub in lin:
                temp.append(sub)
                tempIndex = tempIndex + 1
            if lin.__len__() > 1:
                data.format = temp[0]
                data.RecoveredDate = temp[3] + "-" + formatDate(temp[2])
            else:
                mini = True
                data.InstrumentType = lin[0]

            isDate = False

        elif isSerial:

            lin = line.split()
            data.InstrumentNum = lin[lin.__len__() - 1]
            isSerial = False


        elif isSite:

            lin = line.split(":")
            if mini:
                miniv = lin[1].split()
                if miniv[miniv.__len__() - 1].replace("\n", "").isdigit():
                    data.RecoveredDate = miniv[miniv.__len__() - 1].replace("\n", "")
                    newsitename = removeDigit(miniv).split()
                    data.SiteName = checklocation(newsitename)

            else:
                newsitename = removeDigit(lin[1].split()).split()
                data.SiteName = checklocation(newsitename)
            isSite = False
            headerReady = True


        elif headerReady:

            # Checks if identical data exists in database.
            checkMeta = isMeta(data)

            # Deployment Table
            if checkMeta[0] == 'false':
                c.execute(
                    "INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                    " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                    " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                    " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}', '{df}')" \
                    .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                            sn=data.SiteName.replace("'", ""), itp=data.InstrumentType, lat=data.Latitude,
                            long=data.Longitude, dpd=data.DeploymentDepth, datd=data.DeploymentDate,
                            datt=data.DeploymentTime, recd=data.RecoveredDate, rect=data.TimeOfRecovery,
                            ss=data.SamplingSize, sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

                data.id = c.lastrowid

            # Location Table
            if checkMeta[1] == 'false':
                c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                          " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                          " '{sd}')" \
                          .format(thn='Location', sc=data.SiteCode,
                                  sn=data.SiteName.replace("'", ""),
                                  lat=data.Latitude, long=data.Longitude,
                                  sd=data.DeploymentSiteDepth))

            headerReady = False

        elif count > 14:
            if checkMeta[0] == 'false':
                lin = line.split()
                tempIndex = 0
                temp = []
                for sub in lin:
                    tempIndex = tempIndex + 1
                    if tempIndex > 1:
                        temp.append(sub)

                        if tempIndex > 4:
                            data.data.append(temp)
                            date = data.data[temperatureIndex][3] + "-" + formatDate(data.data[temperatureIndex][2])

                            # Take start date from data
                            if setStartDate:
                                data.DeploymentDate = date
                                data.DeploymentTime = lin[2].replace("'", ":")
                                setStartDate = False
                                c.execute(
                                    """UPDATE Deployments SET StartDate = ? ,StartTime = ? WHERE id= ? """,
                                    (data.DeploymentDate, data.DeploymentTime, data.id))

                            # Data Table
                            c.execute(
                                "INSERT INTO {tn} ('d_id', 'deployment_id', 'Temperature', 'Year', 'Time' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                                    .format(tn='Data', fn=data.id,
                                            tv=data.data[temperatureIndex][0].replace("+", ""),
                                            tm=data.data[temperatureIndex][1].replace("'", ".").replace(".", ":"),
                                            yr=date))

                            temperatureIndex = temperatureIndex + 1

    # If data doesn't already exist we can commit to the database
    if checkMeta[0] == 'false':
        conn.commit()  # Commit changes to the DB.
    conn.close()  # Closing connection to the DB.


###########################################################################################################


def read_pipe(datafile):
    print("Pushing " + datafile + " To Database")
    data = Deployments(datafile)
    data.datafile = getFilename(datafile)
    title = datafile.split("_")
    data.InstrumentNum = title[3]
    try:
        f = open(datafile, "r")
    except:
        exit()

    def convertDate(date):

        temp = date.split("-")
        dateN = ""
        if temp[1].__contains__('JAN'):
            dateN = temp[2] + '-01-' + temp[0]

        elif temp[1].__contains__('FEB'):
            dateN = temp[2] + '-02-' + temp[0]

        elif temp[1].__contains__('MAR'):
            dateN = temp[2] + '-03-' + temp[0]

        elif temp[1].__contains__('APR'):
            dateN = temp[2] + '-04-' + temp[0]

        elif temp[1].__contains__('MAY'):
            dateN = temp[2] + '-05-' + temp[0]

        elif temp[1].__contains__('JUN'):
            dateN = temp[2] + '-06-' + temp[0]

        elif temp[1].__contains__('JUL'):
            dateN = temp[2] + '-07-' + temp[0]

        elif temp[1].__contains__('AUG'):
            dateN = temp[2] + '-08-' + temp[0]

        elif temp[1].__contains__('SEP'):
            dateN = temp[2] + '-09-' + temp[0]

        elif temp[1].__contains__('OCT'):
            dateN = temp[2] + '-10-' + temp[0]

        elif temp[1].__contains__('NOV'):
            dateN = temp[2] + '-11-' + temp[0]

        elif temp[1].__contains__('DEC'):
            dateN = temp[2] + '-12-' + temp[0]

        return dateN.encode()

    f.readline()
    read = 'true'
    while (read):
        line = f.readline()

        if line.__contains__('-- DATA --'):  # Data and format were inconsistent, needed to check each line in header
            break

        elif line.__contains__('STATION'):
            data.SiteCode = line.strip().split('=')[1].replace(",", "").replace("'", "")

        elif line.__contains__('LATITUDE'):
            convert = line.strip().replace(",", "").split('=')[1].split()
            data.Latitude = convertLatLong(convert).__str__()

        elif line.__contains__('LONGITUDE'):
            convert = line.strip().replace(",", "").split('=')[1].split()
            data.Longitude = convertLatLong(convert).__str__()

        elif line.__contains__('START_TIME'):

            lin = line.split()
            newDate = ""
            if lin.__len__() > 2:  # For dates that have a " " before a number " 1" instead of "01"
                fixDate = "0" + lin[1]
                newDate = convertDate(fixDate).decode()
                data.DeploymentTime = lin[2].replace(",", "").replace("'", "")
                data.DeploymentDate = newDate

            else:
                data.DeploymentTime = line.strip().split('=')[1].split()[1].replace("'", "").replace(",", "")
                dateS = line.strip().split('=')[1].split()[0].replace("'", "")
                newDate = convertDate(dateS)
                data.DeploymentDate = newDate.decode()

        elif line.__contains__('END_TIME'):
            lin = line.split()
            newDate = ""
            if lin.__len__() > 2:
                fixDate = "0" + lin[1]
                newDate = convertDate(fixDate).decode()
                data.TimeOfRecovery = lin[2].replace(",", "").replace("'", "")
                data.RecoveredDate = newDate

            else:
                data.TimeOfRecovery = line.strip().split('=')[1].split()[1].replace("'", "").replace(",", "")
                dateS = line.strip().split('=')[1].split()[0].replace("'", "")
                newDate = convertDate(dateS)
                data.RecoveredDate = newDate.decode()

        elif line.__contains__('SAMPLING'):
            data.SamplingSize = line.split('=')[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_DEPTH'):
            data.DeploymentDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('WATER_DEPTH'):
            data.DeploymentSiteDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_TYPE'):
            data.InstrumentType = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                 "").rstrip()

    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Checks if identical data exists in database.
    checkMeta = isMeta(data)

    # Deployment Table
    if checkMeta[0] == 'false':
        c.execute("INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                  " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                  " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                  " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}','{df}')" \
                  .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                          sn=data.SiteName, itp=data.InstrumentType, lat=data.Latitude, long=data.Longitude,
                          dpd=data.DeploymentDepth, datd=data.DeploymentDate, datt=data.DeploymentTime,
                          recd=data.RecoveredDate, rect=data.TimeOfRecovery, ss=data.SamplingSize,
                          sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

        data.id = c.lastrowid

        for lin in f:
            l = lin.split()
            data.data.append(l)
            if l[0] == "'":  # Handling black spaces in the dates
                tempDate = "0" + l[1].replace("'", "")
                dataDate = convertDate(tempDate).decode()
                dataTime = l[2].replace("'", "").replace(".", ":")
                dataTemp = l[3].replace("'", "")
            else:
                tempDate = l[0].replace("'", "")
                dataDate = convertDate(tempDate).decode()
                dataTime = l[1].replace("'", "").replace(".", ":")
                dataTemp = l[2].replace("'", "")

            # Data Table
            c.execute(
                "INSERT INTO {tn} ('d_id', 'deployment_id','{tc}', '{yc}', '{tic}' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                    .format(tn='Data', tic='Time', tc='Temperature', fn=data.id,
                            tv=dataTemp.replace("+", ""),
                            tm=dataTime,
                            yr=dataDate,
                            yc='Year'))
        conn.commit()

    # Location Table
    if checkMeta[1] == 'false':
        c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                  " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                  " '{sd}')" \
                  .format(thn='Location', sc=data.SiteCode,
                          sn=data.SiteName.replace("'", ""),
                          lat=data.Latitude, long=data.Longitude,
                          sd=data.DeploymentSiteDepth))

        conn.commit()

    conn.close()  # Closing connection to the DB.


###########################################################################################################


def read_rpf(datafile):
    print("Pushing " + datafile + " To Database")
    data = Deployments(datafile)
    data.datafile = getFilename(datafile)
    try:
        f = open(datafile, "r")
    except:
        exit()

    f.readline()
    read = 'true'
    while (read):
        line = f.readline()

        if line.replace("\n", "").__contains__(
                '-- DATA --'):  # Data and format were inconsistent, needed to check each line in header
            break

        elif line.__contains__('STATION'):
            data.SiteCode = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('SITE_NAME'):
            data.SiteName = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('LATITUDE'):
            data.Latitude = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('LONGITUDE'):
            data.Longitude = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('START_DATE'):
            data.DeploymentDate = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('START_TIME'):
            data.DeploymentTime = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('END_DATE'):
            data.RecoveredDate = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('END_TIME'):
            data.TimeOfRecovery = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('SAMPLING_INTERVAL'):
            data.SamplingSize = line.split('=')[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_DEPTH'):
            data.DeploymentDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('WATER_DEPTH'):
            data.DeploymentSiteDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_TYPE'):
            data.InstrumentType = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                 "").rstrip()

        elif line.__contains__('SERIAL_NUMBER'):
            data.InstrumentNum = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                 "").rstrip()

    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Checks if identical data exists in database.
    checkMeta = isMeta(data)

    if checkMeta[0] == 'false':
        # Deployment Table
        c.execute("INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                  " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                  " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                  " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}','{df}')" \
                  .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                          sn=data.SiteName, itp=data.InstrumentType, lat=data.Latitude, long=data.Longitude,
                          dpd=data.DeploymentDepth, datd=data.DeploymentDate, datt=data.DeploymentTime,
                          recd=data.RecoveredDate, rect=data.TimeOfRecovery, ss=data.SamplingSize,
                          sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

        data.id = c.lastrowid
        for lin in f:
            l = lin.split()
            data.data.append(l)
            dataDate = l[0].replace("'", "")
            dataTime = l[1].replace("'", "")
            dataTemp = l[2].replace("'", "")

            # Data Table
            c.execute(
                "INSERT INTO {tn} ('d_id', 'deployment_id','{tc}', '{yc}', '{tic}' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                    .format(tn='Data', tic='Time', tc='Temperature', fn=data.id,
                            tv=dataTemp.replace("+", ""),
                            tm=dataTime,
                            yr=dataDate,
                            yc='Year'))

        conn.commit()

    # Location Table
    if checkMeta[1] == 'false':
        c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                  " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                  " '{sd}')" \
                  .format(thn='Location', sc=data.SiteCode,
                          sn=data.SiteName.replace("'", ""),
                          lat=data.Latitude, long=data.Longitude,
                          sd=data.DeploymentSiteDepth))

        conn.commit()

    conn.close()  # Closing connection to the DB.


###########################################################################################################


def read_json(datafile):
    print("Pushing " + datafile + " To Database")

    data = Deployments(datafile)
    data.datafile = getFilename(datafile)
    try:
        f = open(datafile, "r")
    except:
        exit()
    info = json.load(f)
    data.SiteCode = info["HEADER"]["STATION"]
    data.SiteName = info["HEADER"]["SITE_NAME"]
    data.DeploymentDate = info["HEADER"]["START_DATE"]
    data.DeploymentTime = info["HEADER"]["START_TIME"]
    data.RecoveredDate = info["HEADER"]["END_DATE"]
    data.TimeOfRecovery = info["HEADER"]["END_TIME"]
    data.Latitude = info["HEADER"]["LATITUDE"]
    data.Longitude = info["HEADER"]["LONGITUDE"]
    data.InstrumentType = info["HEADER"]["INST_TYPE"]
    data.InstrumentNum = info["HEADER"]["SERIAL_NUMBER"]
    data.DeploymentSiteDepth = info["HEADER"]["WATER_DEPTH"]
    data.DeploymentDepth = info["HEADER"]["INST_DEPTH"]
    data.SamplingSize = info["HEADER"]["SAMPLING_INTERVAL"]

    sqlite_file = data.directory
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()

    # Checks if identical data exists in database.
    checkMeta = isMeta(data)

    if checkMeta[0] == 'false':
        # Deployment Table
        c.execute("INSERT INTO '{thn}' ('id', 'SerialNumber', 'SiteCode', 'SiteName', 'InstrumentType', 'Latitude',"
                  " 'Longitude', 'DeploymentDepth', 'StartDate', 'StartTime', 'EndDate', 'EndTime', 'SamplingSize',"
                  " 'SiteDepth', 'CreationDate', 'File') VALUES ( NULL, '{inum}', '{sc}', '{sn}', '{itp}', '{lat}', '{long}', '{dpd}', '{datd}', "
                  " '{datt}', '{recd}', '{rect}', '{ss}', '{sd}', '{cd}','{df}')" \
                  .format(thn='Deployments', did=data.id, inum=data.InstrumentNum, sc=data.SiteCode,
                          sn=data.SiteName, itp=data.InstrumentType, lat=data.Latitude, long=data.Longitude,
                          dpd=data.DeploymentDepth, datd=data.DeploymentDate, datt=data.DeploymentTime,
                          recd=data.RecoveredDate, rect=data.TimeOfRecovery, ss=data.SamplingSize,
                          sd=data.DeploymentSiteDepth, df=data.datafile, cd=data.creationDate))

        data.id = c.lastrowid

        for lin in info["DATA"]:
            datadate = lin[0].split()[0]
            datatime = lin[0].split()[1]
            datatemp = lin[1].__str__()
            # Data Table
            c.execute(
                "INSERT INTO {tn} ('d_id', 'deployment_id','{tc}', '{yc}', '{tic}' ) VALUES (NULL, '{fn}', '{tv}','{yr}', '{tm}' )" \
                    .format(tn='Data', tic='Time', tc='Temperature', yc='Year', fn=data.id,
                            tv=datatemp.replace("+", ""),
                            tm=datatime,
                            yr=datadate,
                            ))
        conn.commit()

    # Location Table
    if checkMeta[1] == 'false':
        c.execute("INSERT INTO '{thn}' ('loc_id', 'SiteCode', 'SiteName', 'Latitude',"
                  " 'Longitude','SiteDepth') VALUES (NULL, '{sc}', '{sn}', '{lat}', '{long}',"
                  " '{sd}')" \
                  .format(thn='Location', sc=data.SiteCode,
                          sn=data.SiteName.replace("'", ""),
                          lat=data.Latitude, long=data.Longitude,
                          sd=data.DeploymentSiteDepth))

        conn.commit()

    conn.close()  # Closing connection to the DB.


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


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    dir_path = os.path.dirname(os.path.realpath(__file__))
    pathname = dir_path.replace("\\", '/').split('/')

    DatabaseFile = 'thermo.db'
    selection = input("Current Database Path: " + DatabaseFile + "\nWould you like to change the Database?    Y / N")

    if selection.lower() == "n":
        DatabaseFile = "thermo.db"
    else:
        DatabaseFile = input("Enter New Database Path: ")

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)


    filename = pathname[pathname.__len__() - 1]


    files = getListOfFiles(dirName)
    for f in files:
        datafile = f
        if datafile.lower().endswith(".dat"):
            read_hugrun(datafile)

        elif datafile.lower().endswith(".pro"):
            read_pro(datafile)

        elif datafile.lower().endswith(".pipe"):
            read_pipe(datafile)

        elif datafile.lower().endswith(".csv"):
            read_mini_two(datafile)

        elif datafile.lower().endswith(".rpf"):
            read_rpf(datafile)

        elif datafile.lower().endswith(".json"):
            read_json(datafile)

        elif datafile.lower().__contains__("asc"):
            read_mini_one(datafile)

        else:
            print("File Not Supported...")

    print("******************************")