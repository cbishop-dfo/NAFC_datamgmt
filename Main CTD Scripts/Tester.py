from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import pandas as pd
import seawater as sw






def StandardizedDF(df):
    newdf = pd.DataFrame()

    # for c in cast.ColumnNames:
    for c in col:
        name = c.replace("/", "+")
        if c.lower().__eq__('prdm'):
            newdf['Pressure'] = df[c].values

        elif c.lower().__eq__('t090c'):
            newdf['Temperature'] = df[c].values

        elif c.lower().__eq__('t190c'):
            newdf['Secondary Temperature'] = df[c].values

        elif c.lower().__eq__('c0s/m'):
            newdf['Conductivity'] = df[c].values

        elif c.lower().__eq__('c1s/m'):
            newdf['Secondary Conductivity'] = df[c].values

        elif c.lower().__eq__('cond'):
            newdf['Conductivity'] = df[c].values

        elif c.lower().__eq__('cstarat0'):
            newdf['Transmissometer attenuation'] = df[c].values

        elif c.lower().__eq__('cstartr0'):
            newdf['Transmissometer transmission'] = df[c].values

        elif c.lower().__eq__('depth'):
            newdf['Depth'] = df[c].values

        elif c.lower().__eq__('flag'):
            newdf['Flag'] = df[c].values

        elif c.lower().__eq__('fleco-afl'):
            newdf['Chlorophyll A Fluorescence'] = df[c].values

        elif c.lower().__eq__('flor'):
            newdf['Fluorescence'] = df[c].values

        elif c.lower().__eq__('oxsatml/l'):
            newdf['Oxygen Saturation'] = df[c].values

        elif c.lower().__eq__('oxy'):
            newdf['Oxygen Saturation'] = df[c].values

        elif c.lower().__eq__('par'):
            newdf['Irradiance'] = df[c].values

        elif c.lower().__eq__('par/sat/log'):
            newdf['Photosynthetic Active Radiation'] = df[c].values

        elif c.lower().__eq__('ph'):
            newdf['pH'] = df[c].values

        elif c.lower().__eq__('pres'):
            newdf['Pressure'] = df[c].values

        elif c.lower().__eq__('sal'):
            newdf['Salinity'] = df[c].values

        elif c.lower().__eq__('sal00'):
            newdf['Salinity'] = df[c].values

        elif c.lower().__eq__('sal11'):
            newdf['Secondary Salinity'] = df[c].values

        elif c.lower().__eq__('sbeox0ml/l'):
            newdf['Oxygen'] = df[c].values

        elif c.lower().__eq__('sbeox0v'):
            newdf['Oxygen Raw'] = df[c].values

        elif c.lower().__eq__('sbeox1ml/l'):
            newdf['Secondary Oxygen'] = df[c].values

        elif c.lower().__eq__('sbeox1v'):
            newdf['Secondary Oxygen Raw'] = df[c].values

        elif c.lower().__eq__('scan'):
            newdf['scan'] = df[c].values
            continue
            # Dictionary['Scan'] = [nc_out.createVariable('Scan', np.float32, ('level'), zlib=True, fill_value=-9999), name]

        elif c.lower().__eq__('sigma-t00'):
            newdf['Density'] = df[c].values

        elif c.lower().__eq__('sigma-t11'):
            newdf['Secondary Density'] = df[c].values

        elif c.lower().__eq__('sigt'):
            newdf['Density'] = df[c].values

        elif c.lower().__eq__('temp'):
            newdf['Temperature'] = df[c].values

        elif c.lower().__eq__('wetcdom'):
            newdf['CDOM Fluorescence'] = df[c].values

        elif c.lower().__eq__('depsm'):
            newdf['Depth'] = df[c].values

        else:
            newdf[c] = df[c].values
            print("UNKNOWN VARIABLE: " + c.__str__())\

    return newdf



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

            # df_press_depth creates a dataframe with both pressure and depth
            df = cnv_tk.df_press_depth(cast)
            col = df.columns._values

            # StandardizedDF takes an existing dataframe and returns a df with converted column names to match Midlayer.
            sdf = cnv_tk.StandardizedDF(df)
            print()



