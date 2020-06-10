import sqlite3
from sqlite3 import Error
import datetime

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
        self.directory = 'D:/Thermo_db.sqlite'  # DB Location.

        # CRUISE_HEADER **************************************
        self.countrycode = "1805"
        self.crusenumber = ""
        self.orginization = "DFO NAFC"
        self.cruiseStart = ""
        self.cruiseEnd = ""
        self.chiefSci = ""
        self.platform = ""
        self.cruiseName = ""
        self.cruiseDescription = ""

        # EVENT_HEADER ***************************************
        self.eventType = "MTR"
        self.eventNumber = ""
        self.eventQualifier1 = ""
        self.eventQualifier2 = ""
        self.eventCreationDate = datetime.datetime.now().isoformat().replace("T", " ")
        self.eventOrigCreationDate = ""
        self.eventStartDateTime = "17-NOV-1858 00:00:00.00"
        self.eventEndDateTime = "17-NOV-1858 00:00:00.00"
        self.eventInitLat = "-99.0"
        self.eventInitLong = "999.9"
        self.eventEndLat = "-99.0"
        self.eventEndLong = "999.9"
        self.eventMinDepth = ""
        self.eventMaxDepth = ""
        self.eventSounding = "-99.0"
        self.eventBottomDepth = "-99.0"
        self.eventComments = ""

        # INSTRUMENT_HEADER **********************************
        self.INST_TYPE = "Thermograph"
        self.MODEL = "null"
        self.instrumentDescription = ""

        # PARAMETER_HEADER ***********************************
        self.parType = ""
        self.parName = ""
        self.parUnits = "Degrees C"
        self.parCode = ""
        self.nullValue = "-99.0"
        self.parPrintFieldWidth = ""
        self.parPrintDecimalPlace = ""
        self.parAngleOfSelection = ""
        self.parMagVar = ""
        self.parDepth = ""
        self.parMinVal = ""
        self.parMaxVal = ""
        self.parNumValid = ""
        self.parNumNull = ""

        # RECORD_HEADER **************************************
        self.recNumCal = ""
        self.recNumSwing = ""
        self.recNumHistory = ""
        self.recNumCycle = ""
        self.recNumParam = ""


###########################################################################################################

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        print(err)


###########################################################################################################


def fixTemperature(temperature):
    temperature = temperature.replace("+", "")  # '+' before the number throws error for json
    if temperature.startswith("."):  # starting with a '.' also causes an error
        temperature = "0" + temperature

    elif temperature.startswith("-."):  # '-' is valid so long as it's not '-.'
        temperature = temperature.replace("-.", "-0.")

    return temperature


###########################################################################################################


def write_json(conn):
    data = Deployments()
    c = conn.cursor()
    c.execute("SELECT * FROM Deployments")
    rows = c.fetchall()

    for row in rows:
        data.id = row[0]
        data.InstrumentType = row[1]
        data.SiteName = row[3]
        data.SiteCode = row[4]
        data.InstrumentNum = row[2]
        data.Latitude = row[5]
        data.Longitude = row[6]
        data.DeploymentDate = row[7]
        data.DeploymentTime = row[8]
        data.RecoveredDate = row[9]
        data.TimeOfRecovery = row[10]
        data.SamplingSize = row[13]
        data.DeploymentSiteDepth = row[11]
        data.DeploymentDepth = row[12]
        # Creating the file name based on the deployment ID and the deployment date.
        f = open("MTR_" + data.id.__str__() + "_" + data.DeploymentDate.replace("-", "_").replace("/", "_") + ".json",
                 "w+")

        f.write(
            "{\n" +
            '  "HEADER" :  {\n' +
            '       "STATION" : "' + data.SiteCode + '",' + "\n" +
            '       "SITE_NAME": "' + data.SiteName + '",' + "\n" +
            '       "START_DATE" : "' + data.DeploymentDate.replace("/", "-") + '",' + "\n" +
            '       "START_TIME" : "' + data.DeploymentTime + '",' + "\n" +
            '       "END_DATE" : "' + data.RecoveredDate.replace("/", "-") + '",' + "\n" +
            '       "END_TIME" : "' + data.TimeOfRecovery + '",' + "\n" +
            '       "LATITUDE" : "' + data.Latitude + '",' + "\n" +
            '       "LONGITUDE" : "' + data.Longitude + '",' + "\n" +
            '       "INST_TYPE" : "' + data.InstrumentType + '",' + "\n" +
            '       "SERIAL_NUMBER" : "' + data.InstrumentNum + '",' + "\n" +
            '       "WATER_DEPTH" : "' + data.DeploymentSiteDepth + '",' + "\n" +
            '       "INST_DEPTH" : "' + data.DeploymentDepth + '",' + "\n" +
            '       "SAMPLING_INTERVAL" : "' + data.SamplingSize + '"' + "\n" + "  },\n" + '  "DATA" : [\n')

        d = conn.cursor()
        rowid = row[0]
        d.execute("select * from Data where deployment_id is '{dv}'".format(dv=rowid))
        datar = d.fetchall()
        for dat in datar:
            data.data.append(dat)
            datatemperature = fixTemperature(dat[2])
            datatime = dat[3]
            datadate = dat[4]
            f.write('       [\n         "'
                    + datadate
                    + " "
                    + datatime
                    + '",\n         ' + datatemperature + "\n       ]")

            if not dat == datar[datar.__len__() - 1]:
                f.write(",\n")

        f.write("\n  ]\n")
        f.write("}")


###########################################################################################################


def write_rpf(conn):
    data = Deployments()
    c = conn.cursor()
    c.execute("SELECT * FROM Deployments")
    rows = c.fetchall()

    for row in rows:
        data.id = row[0]
        data.InstrumentType = row[1]
        data.SiteName = row[3]
        data.SiteCode = row[4]
        data.InstrumentNum = row[2]
        data.Latitude = row[5]
        data.Longitude = row[6]
        data.DeploymentDate = row[7]
        data.DeploymentTime = row[8]
        data.RecoveredDate = row[9]
        data.TimeOfRecovery = row[10]
        data.SamplingSize = row[13]
        data.DeploymentSiteDepth = row[11]
        data.DeploymentDepth = row[12]
        # Creating the file name based on the deployment ID and the deployment date.
        f = open("MTR_" + data.id.__str__() + "_" + data.DeploymentDate.replace("-", "_").replace("/", "_") + ".rpf",
                 "w+")

        f.write(
            "HEADER,\n" +
            "   STATION=" + data.SiteCode + "," + "\n" +
            "   SITE_NAME=" + data.SiteName + "," + "\n" +
            "   START_DATE=" + data.DeploymentDate.replace("/", "-") + "," + "\n" +
            "   START_TIME=" + data.DeploymentTime + "," + "\n" +
            "   END_DATE=" + data.RecoveredDate.replace("/", "-") + "," + "\n" +
            "   END_TIME=" + data.TimeOfRecovery + "," + "\n" +
            "   LATITUDE=" + data.Latitude + "," + "\n" +
            "   LONGITUDE=" + data.Longitude + "," + "\n" +
            "   INST_TYPE=" + data.InstrumentType + "," + "\n" +
            "   SERIAL_NUMBER=" + data.InstrumentNum + "," + "\n" +
            "   WATER_DEPTH=" + data.DeploymentSiteDepth + "," + "\n" +
            "   INST_DEPTH=" + data.DeploymentDepth + "\n" +
            "   SAMPLING_INTERVAL=" + data.SamplingSize + "\n" + "-- DATA --\n")

        d = conn.cursor()
        rowid = row[0]
        d.execute("select * from Data where deployment_id is '{dv}'".format(dv=rowid))
        datar = d.fetchall()
        for dat in datar:
            data.data.append(dat)
            f.write(data.data[data.data.__len__() - 1][4] + " " + data.data[data.data.__len__() - 1][3] + " " +
                    data.data[data.data.__len__() - 1][2] + "\n")


###########################################################################################################


def write_ODF(conn):
    data = Deployments()
    c = conn.cursor()
    c.execute("SELECT * FROM Deployments")
    rows = c.fetchall()

    for row in rows:
        data.id = row[0]
        data.MODEL = row[1]
        data.SiteName = row[3]
        data.SiteCode = row[4]
        data.InstrumentNum = row[2]
        data.eventQualifier2 = row[2]
        data.Latitude = row[5]
        data.eventInitLat = row[5]
        data.eventEndLat = row[5]
        data.Longitude = row[6]
        data.eventInitLong = row[6]
        data.eventEndLong = row[6]  # Assuming Instrument Started and ended in the same location.
        data.DeploymentDate = row[7]
        data.DeploymentTime = row[8]
        data.eventQualifier1 = row[8]
        data.RecoveredDate = row[9]
        data.TimeOfRecovery = row[10]
        data.DeploymentSiteDepth = row[11]
        data.DeploymentDepth = row[12]
        data.SamplingSize = row[13]
        data.eventCreationDate = row[14]
        # Creating the file name based on the deployment ID and the deployment date.
        f = open("MTR_" + data.id.__str__() + "_" + data.DeploymentDate.replace("-", "_").replace("/", "_") + ".ODF",
                 "w+")
        datafile = f.name

        f.write(
            "ODF_HEADER,\n" +
            "   FILE_SPECIFICATION='" + datafile + "'\n" +

            # CRUISE_HEADER **************************************
            "CRUISE_HEADER,\n" +
            "   COUNTRY_INSTITUTE_CODE=" + data.countrycode + ",\n" +
            "   CRUISE_NUMBER='" + data.crusenumber + "',\n" +
            "   ORGANIZATION='" + data.orginization + "',\n" +
            "   CHIEF_SCIENTIST='" + data.chiefSci + "',\n" +
            "   START_DATE='" + data.cruiseStart + "',\n" +
            "   END_DATE='" + data.cruiseEnd + "',\n" +
            "   PLATFORM='" + data.platform + "',\n" +
            "   CRUISE_NAME='" + data.cruiseName + "',\n" +
            "   CRUISE_DESCRIPTION='" + data.cruiseDescription + "'\n" +

            # EVENT_HEADER **************************************
            "EVENT_HEADER,\n" +
            "   DATA_TYPE='" + data.eventType + "',\n" +
            "   EVENT_NUMBER='" + data.eventNumber + "',\n" +
            "   EVENT_QUALIFIER1='" + data.eventQualifier1 + "',\n" +
            "   EVENT_QUALIFIER2='" + data.eventQualifier2 + "',\n" +
            "   CREATION_DATE='" + data.eventCreationDate + "',\n" +
            "   ORIG_CREATION_DATE='" + data.eventOrigCreationDate + "',\n" +
            "   START_DATE_TIME='" + data.DeploymentDate + " " + data.DeploymentTime + "',\n" +
            "   END_DATE_TIME='" + data.RecoveredDate + " " + data.TimeOfRecovery + "',\n" +
            "   INITIAL_LATITUDE=" + data.eventInitLat + ",\n" +
            "   INITIAL_LONGITUDE=" + data.eventInitLong + ",\n" +
            "   END_LATITUDE=" + data.eventEndLat + ",\n" +
            "   END_LONGITUDE=" + data.eventEndLong + ",\n" +
            "   MIN_DEPTH=" + data.eventMinDepth + ",\n" +
            "   MAX_DEPTH=" + data.eventMaxDepth + ",\n" +
            "   SAMPLING_INTERVAL=" + data.SamplingSize + ",\n" +
            "   SOUNDING=" + data.eventSounding + ",\n" +
            "   DEPTH_OFF_BOTTOM=" + data.eventBottomDepth + ",\n" +
            "   EVENT_COMMENTS='" + data.eventComments + "'\n" +

            # INSTRUMENT_HEADER **********************************
            "INSTRUMENT_HEADER,\n" +
            "   INST_TYPE='" + data.INST_TYPE + "'," + "\n" +
            "   MODEL='" + data.MODEL + "',\n" +
            "   SERIAL_NUMBER='" + data.InstrumentNum + "'," + "\n" +
            "   DESCRIPTION='" + data.instrumentDescription + "'\n" +

            # PARAMETER_HEADER ***********************************
            "PARAMETER_HEADER,\n" +
            "   TYPE='" + data.parType + "',\n" +
            "   NAME='" + data.parName + "',\n" +
            "   UNITS='" + data.parUnits + "',\n" +
            "   CODE='" + data.parCode + "',\n" +
            "   NULL_VALUE='" + data.nullValue + "',\n" +
            "   PRINT_FIELD_WIDTH=" + data.parPrintFieldWidth + ",\n" +
            "   PRINT_DECIMAL_PLACES=" + data.parPrintDecimalPlace + ",\n" +
            "   ANGLE_OF_SECTION=" + data.parAngleOfSelection + ",\n" +
            "   MAGNETIC_VARIATION=" + data.parMagVar + ",\n" +
            "   DEPTH=" + data.parDepth + ",\n" +
            "   MINIMUM_VALUE=" + data.parMinVal + ",\n" +
            "   MAXIMUM_VALUE=" + data.parMaxVal + ",\n" +
            "   NUMBER_VALID=" + data.parNumValid + ",\n" +
            "   NUMBER_NULL=" + data.parNumNull + "\n" +

            # RECORD_HEADER **************************************
            "RECORD_HEADER,\n" +
            "   NUM_CALIBRATION=" + data.recNumCal + ",\n" +
            "   NUM_SWING=" + data.recNumSwing + ",\n" +
            "   NUM_HISTORY=" + data.recNumHistory + ",\n" +
            "   NUM_CYCLE=" + data.recNumCycle + ",\n" +
            "   NUM_PARAM=" + data.recNumParam + "\n" + "-- DATA --\n")

        d = conn.cursor()
        rowid = row[0]
        d.execute("select * from Data where deployment_id is '{dv}'".format(dv=rowid))
        datar = d.fetchall()
        for dat in datar:
            data.data.append(dat)
            f.write("'" + data.data[data.data.__len__() - 1][4] + " " + data.data[data.data.__len__() - 1][3] + "' "
                    + data.data[data.data.__len__() - 1][2].replace("+", "") + "\n")


###########################################################################################################


def main():
    def launchwriter():
        print("Select Format:")
        print("[1] JSON")
        print("[2] Revised Pipe")
        print("[3] ODF")
        print("\nPress [q] To Quit")
        select = input()
        with conn:
            if select == "1":
                print("Format Selected: JSON")
                write_json(conn)

            elif select == "2":
                print("Format Selected: Revised Pipe Format (rpf)")
                write_rpf(conn)

            elif select == "3":
                print("Format Selected: Ocean Data Format (ODF)")
                write_ODF(conn)

            elif select.lower() == "q":
                print("Quiting...")
                exit()

            else:
                print("Please Select [1], [2], [3], or [q]")
                launchwriter()

    def setDirectory():
        # default path
        database = 'Thermo_db.sqlite'

        print("Would you like to change database?")
        print(" Current path: " + database + "\n y/n")
        select = input()
        if select.lower() == "y":
            print("Input new path:")
            database = input()
            print("\nNew Path: " + database + "\n")
            return database
        elif select.lower() == "n":
            return database
        else:
            print("Please Choose y or n...\n")
            setDirectory()

    database = setDirectory()
    conn = create_connection(database)
    launchwriter()
    conn.close()


if __name__ == '__main__':
    main()
