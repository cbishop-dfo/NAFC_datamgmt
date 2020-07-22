import os
import sqlite3
import pandas as pd
from sqlite3 import Error
import netCDF4 as nc
import numpy as np
import time as tt
import datetime
import xlrd
import csv

__author__ = 'KennedyDyl'
"""
Script to read CTD files from a sqlite database and write out the files into "Revised" subfolder.
created by Dylan Kennedy, 2019-08-20

User will be prompted to change Default database on execution, default is CTD.db.
Once database is chosen user can select output format.
Formats include:

1) SBE format
2) P format
3) RSBE format (Revised SBE)
4) NETCDF format
5) Meteorological

After format is selected, user can choose to write out all files in the database or write out a single file.
All file will be written to a sub folder called "Revised" located inside the working directory.

************************************************************************************************************************
NOTE: For Met data related to the sbe files, the xlsx files need to be in the same directory as the running script.
************************************************************************************************************************
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
        self.setNumber = "   "
        self.castType = " "
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

        # Data arrays
        self.data = []
        self.history = []
        self.channel = []
        self.header = []
        self.software = []
        self.userInput = []
        self.InstrumentInfo = []

###########################################################################################################

# Creates connection to database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        print(err)


###########################################################################################################

def writeCastObject(cast, SBE = False, P = False, RSBE = False, NETCDF=False):

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
        cast.FishSet = row[10]
        cast.CastType = row[11]
        cast.comment = row[12]
        cast.NumScans = row[13]
        cast.SamplingRate = row[14]
        cast.FileType = row[15]
        cast.ChannelCount = row[16]
        cast.DataChannels = row[17]
        cast.Downcast = row[18]
        cast.Subsample = row[19]
        cast.MinDepth = row[20]
        cast.MaxDepth = row[21]
        cast.FishingStrata = row[22]
        cast.metData = row[23]
        cast.CastDatetime = row[24]
        cast.File = row[25]
        cast.Language = row[26]
        cast.Encoding = row[27]
        cast.Contact = row[28]
        cast.Country = row[29]
        cast.MaintenanceContact = row[30]
        cast.OrgName = row[31]
        cast.DataLimit = row[32]

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


def createFolder(foldername):
    current_path = os.path.dirname(os.path.realpath(__file__))
    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\" + foldername + "\\"
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    # Changes dir
    os.chdir(newpath)

###########################################################################################################

def write_mfc(conn):
    c = conn.cursor()
    qry = "Select cid, Ship, Latitude, Longitude, CastDatetime, Cloud, WinDir, WinSPD, wwCode, BarPres, TempWet, TempDry, WavPeroid, WavHeight, SwellDir, SwellPeroid, SwellHeight, IceConc, IceStage, IceBerg, Comment" \
          " From Casts, Meteor" \
          " Where Meteor.cid = Casts.id;"

    # Creating the data frame from our Query.
    df = pd.read_sql_query(qry, conn)

    # List to hold all the ship names to later be added to the data frame.
    ShipNamesForDF = []

    for shipNumber in df["Ship"]:
        Ships = open("ships.txt")
        nameFound = False
        for shipName in Ships:
            number = shipName.replace("\n", "").split()[0]
            try:
                name = shipName.replace("\n", "").split()[1]
            except:
                name = "No Name In List"
                continue

            if number == shipNumber:
                ShipNamesForDF.append(name)
                nameFound = True
                break

        if not nameFound:
            ShipNamesForDF.append("Number Not In List")
    # adding the ship names to the data frame.
    df["ShipName"] = ShipNamesForDF


    #df[column] = Dictionary[column]
    #rows = c.fetchall()

    with open("MeteorData.csv", 'w+', newline='') as csvFile:
        writer = csv.writer(csvFile)
        df.to_csv(csvFile)
        #writer.writerow(df)

###########################################################################################################


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path



    def setDirectory():
        # default path
        database = 'CTD.db'

        print("Would you like to change database?")
        print(" Current path: " + database + "\n [1] Yes / [0] No")
        select = input()
        if int(select) == 1:
            print("Input new path:")
            database = input()
            print("\nNew Path: " + database + "\n")
            return database
        elif int(select) == 0:
            return database
        else:
            print("Please Choose [1] Yes / [0] No ...\n")
            setDirectory()

    def setFileoutput():
        fileFormat = input("Select Format:\n[1] SBE File\n[2] P File\n[3] RSBE File\n[4] NETCDF File\n[5] Meteorological\n")
        if int(fileFormat) == 1:
            print("SBE Format Selected")
            writeCastObject(cast, SBE=True)

        elif int(fileFormat) == 2:
            print("P Format Selected")
            writeCastObject(cast, P=True)

        elif int(fileFormat) == 3:
            print("RSBE Format Selected")
            writeCastObject(cast, RSBE=True)

        elif int(fileFormat) == 4:
            print("RSBE Format Selected")
            writeCastObject(cast, NETCDF=True)

        elif int(fileFormat) == 5:
            print("Meteorological")
            write_mfc(conn)

        else:
            setFileoutput()

    cast = Cast()
    database = setDirectory()
    conn = create_connection(database)
    setFileoutput()


    conn.close()