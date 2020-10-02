import sys
sys.path.append('C://Users//dylan//PycharmProjects//Workspace//Git')
# sys.path.append('C://Users//dylan//PycharmProjects//Workspace//Git//Toolkits')
# sys.path.append('C://Users//dylan//PycharmProjects//Workspace//Git//Resources')
from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import datetime
import time as tt
import numpy as np
import pandas as pd

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
    # s = df.values.shape[0]
    # newpres = []
    # for s in range(s):
    #    newpres.append(s + 1)

    # Replace mean pressures with bin values
    df[cast.ColumnNames[pressureIndex]] = depths

    # Drop all empty rows
    df = df.dropna(axis=0)

    return df


def NCWrite(cast, df):
    """
    Takes Cast object and dataframe and creates a NETCDF using a standard naming scheme for the variables
    Variable names are converted to a standard name from cast.ColumnNames which is populated during function call
    df = cnv_tk.cnv_to_dataframe(cast)

    To create and populate needed params:
    cast = cnv_tk.Cast(datafile)        # Creates an empty Cast type object
    cnv_tk.cnv_meta(cast, datafile)     # Populates meta variables and data arrays within the Cast object
    df = cnv_tk.cnv_to_dataframe(cast)  # Creates and returns a pandas dataframe using data from cast

    :param cast:
    :param df:
    :return:
    """
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

    Dictionary = {}
    for c in cast.ColumnNames:
        name = c.replace("/", "+")
        if c.lower().__eq__('prdm'):
            Dictionary['Pressure'] = [
                nc_out.createVariable('Pressure', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('t090c'):
            Dictionary['Temperature'] = [
                nc_out.createVariable('Temperature', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('t190c'):
            Dictionary['Secondary Temperature'] = [
                nc_out.createVariable('Secondary Temperature', np.float32, ('level'), zlib=True, fill_value=-9999),
                name]

        elif c.lower().__eq__('c0s/m'):
            Dictionary['Conductivity'] = [
                nc_out.createVariable('Conductivity', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('c1s/m'):
            Dictionary['Secondary Conductivity'] = [
                nc_out.createVariable('Secondary Conductivity', np.float32, ('level'), zlib=True, fill_value=-9999),
                name]

        elif c.lower().__eq__('cond'):
            Dictionary['Conductivity'] = [
                nc_out.createVariable('Conductivity', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('cstarat0'):
            Dictionary['Transmissometer attenuation [l per m]'] = [
                nc_out.createVariable('Transmissometer attenuation [l per m]', np.float32, ('level'), zlib=True,
                                      fill_value=-9999), name]

        elif c.lower().__eq__('cstartr0'):
            Dictionary['Transmissometer transmission [%]'] = [
                nc_out.createVariable('Transmissometer transmission [%]', np.float32, ('level'), zlib=True,
                                      fill_value=-9999), name]

        elif c.lower().__eq__('depth'):
            Dictionary['Depth'] = [nc_out.createVariable('Depth', np.float32, ('level'), zlib=True, fill_value=-9999),
                                   name]

        elif c.lower().__eq__('flag'):
            Dictionary['Flag'] = [nc_out.createVariable('Flag', np.float32, ('level'), zlib=True, fill_value=-9999),
                                  name]

        elif c.lower().__eq__('fleco-afl'):
            Dictionary['Chlorophyll A Fluorescence'] = [
                nc_out.createVariable('Chlorophyll A Fluorescence', np.float32, ('level'), zlib=True, fill_value=-9999),
                name]

        elif c.lower().__eq__('flor'):
            Dictionary['Fluorescence'] = [
                nc_out.createVariable('Fluorescence', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('oxsatml/l'):
            Dictionary['Oxygen Saturation'] = [
                nc_out.createVariable('Oxygen Saturation', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('oxy'):
            Dictionary['Oxygen Saturation'] = [
                nc_out.createVariable('Oxygen Saturation', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('par'):
            Dictionary['Irradiance'] = [
                nc_out.createVariable('Irradiance', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('par/sat/log'):
            Dictionary['Photosynthetic Active Radiation'] = [
                nc_out.createVariable('Photosynthetic Active Radiation', np.float32, ('level'), zlib=True,
                                      fill_value=-9999), name]

        elif c.lower().__eq__('ph'):
            Dictionary['pH'] = [nc_out.createVariable('pH', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('pres'):
            Dictionary['Pressure'] = [
                nc_out.createVariable('Pressure', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sal'):
            Dictionary['Salinity'] = [
                nc_out.createVariable('Salinity', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sal00'):
            Dictionary['Salinity'] = [
                nc_out.createVariable('Salinity', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sal11'):
            Dictionary['Secondary Salinity'] = [
                nc_out.createVariable('Secondary Salinity', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sbeox0ml/l'):
            Dictionary['Oxygen'] = [nc_out.createVariable('Oxygen', np.float32, ('level'), zlib=True, fill_value=-9999),
                                    name]

        elif c.lower().__eq__('sbeox0v'):
            Dictionary['Oxygen Raw'] = [
                nc_out.createVariable('Oxygen Raw', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sbeox1ml/l'):
            Dictionary['Secondary Oxygen'] = [
                nc_out.createVariable('Secondary Oxygen', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sbeox1v'):
            Dictionary['Secondary Oxygen Raw'] = [
                nc_out.createVariable('Secondary Oxygen Raw', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('scan'):
            continue
            # Dictionary['Scan'] = [nc_out.createVariable('Scan', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigma-t00'):
            Dictionary['Density'] = [
                nc_out.createVariable('Density', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigma-t11'):
            Dictionary['Secondary Density'] = [
                nc_out.createVariable('Secondary Density', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigt'):
            Dictionary['Density'] = [
                nc_out.createVariable('Density', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('temp'):
            Dictionary['Temperature'] = [
                nc_out.createVariable('Temperature', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('wetcdom'):
            Dictionary['CDOM Fluorescence'] = [
                nc_out.createVariable('CDOM Fluorescence', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('tv290c'):
            Dictionary['Temperature'] = [
                nc_out.createVariable('Temperature', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        else:
            Dictionary[c] = [nc_out.createVariable(name, np.float32, ('level'), zlib=True, fill_value=-9999),
                             name]
            print("UNKNOWN VARIABLE: " + c.__str__())
            input("HALT...Press Enter To Continue")

    times.units = 'hours since 1900-01-01 00:00:00'
    times.calendar = 'gregorian'

    # temp[:] = df["temp"].values
    for d in Dictionary:
        index = Dictionary[d][1]
        index = index.replace("+", "/")
        v = Dictionary[d][0]
        v[:] = df[index].values
        Dictionary[d][0][:] = df[index].values

    # Fill cast info
    latitudes[:] = cast.Latitude
    longitudes[:] = cast.Longitude
    sounder_depths[:] = str(cast.SounderDepth)
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
    Pbin = np.array(df[cast.ColumnNames[pressureIndex]], dtype='float64')
    levels[:] = Pbin
    nc_out.close()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.getListOfFiles(dirName)
    isbinned = input("Would you like the data to be binned?\nY / N\n")
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            # df = modifyDF(cast, df)
            # df = cnv_tk.cnv_sig_dataframe(cast)
            if isbinned.lower().__contains__("y"):
                df = modifyDF(cast, df)
            NCWrite(cast, df)
            # input("Hold, Press enter to load next file")


