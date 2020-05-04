import cnv_tk
import dir_tk
import os
import datetime
import time as tt
import numpy as np
import xarray
import pandas as pd
import sqlite3
try:
    import netCDF4 as nc
except:
    pass
"""
Script that takes a cnv file bins the data and writes out a netcdf file

*IMPORTANT: Scan need to be the first column in the dataframe/datafile in order for modifyDF function to remove upcast. 

"""


def modifyDF(cast, df):

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
    for i in range(0, 1001, 1):
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
    # Here we bin all the data and calculate the mean for each bin
    df = df.groupby(pd.cut(df[cast.ColumnNames[pressureIndex]].astype(float), bins)).mean()
    
    # Had 1 too many values at end
    depths.pop()

    # Create
    #s = df.values.shape[0]
    #newpres = []
    #for s in range(s):
    #    newpres.append(s + 1)

    # Replace mean pressures with bin values
    df[cast.ColumnNames[pressureIndex]] = depths

    # Drop all empty rows
    df = df.dropna(axis=0)

    return df

def NCWrite(cast, df):
    ####################################################################################################
    # NETCDF CREATION HERE:
    ####################################################################################################
    nc_outfile = cast.datafile.replace(".cnv", "").replace(".CNV", "") + "BINNED.nc"
    nc_out = nc.Dataset(nc_outfile, 'w', format='NETCDF3_CLASSIC')
    nc_out.Conventions = 'CF-1.6'
    nc_out.title = 'AZMP netCDF file'
    nc_out.institution = 'Northwest Atlantic Fisheries Centre, Fisheries and Oceans Canada'
    nc_out.source = cast.datafile
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
    #read = conn.cursor()
    #read.execute("SELECT Line FROM Header Where cid like '{castID}'".format(castID=cast.id))
    #header = read.fetchall()
    # TODO: Filter history out of header if necessary.
    history = []
    # Here we are adding all header info into the history
    for h in cast.header:
        history.append(h.__str__().replace('\n', '').replace('(', '').replace(')', '').replace("'", ''))


    num_history_lines = np.size(history)
    # NOTE: ERROR when trying to exec only with map
    # for i in range(0, num_history_lines):
    # exec ('nc_out.processhistory_' + str(i) + ' = ' + ' \' ' + history[i].replace('\n','') + ' \' ')
    # Create dimensions
    time = nc_out.createDimension('time', 1)
    # level = nc_out.createDimension('level', len(df_temp.columns))
    level = nc_out.createDimension('level', df.shape[0])
    # Create coordinate variables
    times = nc_out.createVariable('time', np.float64, ('time',))
    levels = nc_out.createVariable('level', np.float32, ('level',))
    # **** NOTE: Maybe consider using ID instead of time for dimension **** #

    # Create 1D variables
    latitudes = nc_out.createVariable('latitude', np.float32, ('time'), zlib=True)
    longitudes = nc_out.createVariable('longitude', np.float32, ('time'), zlib=True)
    sounder_depths = nc_out.createVariable('sounder_depth', np.float32, ('time'), zlib=True)
    metdata = nc_out.createVariable('metdata', 'c', ('time'), zlib=True)



    Dictionary = {}
    for c in cast.ColumnNames:
        name = c.replace("/", "+")
        Dictionary[c] = [nc_out.createVariable(name, np.float32, ('level'), zlib=True, fill_value=-9999)]
        #cast.ColumnNames.append(c)

    # Create 2D variables
    """
    temp = nc_out.createVariable('temperature', np.float32, ('level'), zlib=True, fill_value=-9999)
    sal = nc_out.createVariable('salinity', np.float32, ('level'), zlib=True, fill_value=-9999)
    cond = nc_out.createVariable('conductivity', np.float32, ('level'), zlib=True, fill_value=-9999)
    sigt = nc_out.createVariable('sigma-t', np.float32, ('level'), zlib=True, fill_value=-9999)
    o2 = nc_out.createVariable('oxygen', np.float32, ('level'), zlib=True, fill_value=-9999)
    fluo = nc_out.createVariable('fluorescence', np.float32, ('level'), zlib=True, fill_value=-9999)
    par = nc_out.createVariable('irradiance', np.float32, ('level'), zlib=True, fill_value=-9999)
    ph = nc_out.createVariable('ph', np.float32, ('level'), zlib=True, fill_value=-9999)
    """
    """
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
    """

    """
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
    """
    times.units = 'hours since 1900-01-01 00:00:00'
    times.calendar = 'gregorian'

    #temp[:] = df["temp"].values
    for d in Dictionary:
        name = d.replace("+", "/")
        x = df[name].values
        v =Dictionary[d][0]
        v[:] = df[name].values
        Dictionary[d][0][:] = df[name].values
        #d[:] = df[d].values
    """
    sal[:] = df["sal"].values
    cond[:] = df["cond"].values
    sigt[:] = df["sigt"].values
    o2[:] = df["oxy"].values
    fluo[:] = df["flor"].values
    par[:] = df["par"].values
    ph[:] = df["pH"].values
    """


    # Fill cast info
    latitudes[:] = cast.Latitude
    longitudes[:] = cast.Longitude
    sounder_depths[:] = str(cast.SounderDepth)
    # Fill time
    try:
        date = datetime.datetime.strptime(cast.CastDatetime, '%Y-%m-%d %H:%M:%S')
    except:
        date = datetime.datetime.strptime(cast.CastDatetime, '%Y-%m-%d %H:%M')
    times[:] = nc.date2num(date, units=times.units, calendar=times.calendar)

    # Typically the pressure/depth index
    pressureIndex = 1
    for row in cast.InstrumentInfo:
        if row.lower().__contains__("pressure") and not cast.isPressure:
            #cast.isPressure = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
        elif row.lower().__contains__("depth") and not cast.isPressure:
            #cast.isPressure = True
            cast.hasDepth = True
            sRow = row.split(" ")
            pressureIndex = int(sRow[2])
            break
    Pbin = np.array(df[cast.ColumnNames[pressureIndex]], dtype='float64')
    levels[:] = Pbin

    #TODO: finish implementing binning here





    """
    ####### ######## ###########

    Tlist = []
    P = np.array(df[cast.ColumnNames[pressureIndex]], dtype='float64')

    Ibtm = np.argmax(P)
    digitized = np.digitize(P[0:Ibtm], Pbin)  # <- this is awesome!

    X = np.array(df['t090C'])
    Tlist.append([X[0:Ibtm][digitized == i].mean() for i in range(0, len(Pbin))])
    print("digitized")


    ####### ######## ###########
    """


    nc_out.close()



if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.getListOfFiles(dirName)
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            #df = modifyDF(cast, df)
            #df = cnv_tk.cnv_sig_dataframe(cast)
            df = modifyDF(cast, df)
            NCWrite(cast, df)
            #input("Hold, Press enter to load next file")


