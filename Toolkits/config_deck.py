import pandas as pd
from Toolkits import cnv_tk
# Creates a df of instrument name, and number and valid data columns to keep
# Creates and returns a pandas dataframe containing deck information
# indexes  ------------------------
# [0] - instrument name
# [1] - instrument number
# [2] - data columns to keep (Note: uses the standardized naming from StandardizedDF(cast, df) from cnv_tk. ie pres is Pressure)
"""
***************************************************
Variable Naming (datafile - standardized)
***************************************************
prdm - Pressure
t090c - Temperature
t190c - Secondary Temperature
c0s/m - Conductivity
c1s/m - Secondary Conductivity
cond - Conductivity
cstarat0 - Transmissometer attenuation
tra - Transmissometer attenuation
cstartr0 - Transmissometer transmission
trp - Transmissometer transmission
depth - Depth
flag - Flag
fleco-afl - Chlorophyll A Fluorescence
flor - Fluorescence
oxsatml/l - Oxygen Saturation
oxy - Oxygen Saturation
par - Irradiance
par/sat/log - Photosynthetic Active Radiation
ph - pH
pres - Pressure
sal - Salinity
sal00 - Salinity
sal11 - Secondary Salinity
sbeox0ml/l - Oxygen
sbeox0v - Oxygen Raw
sbeox1ml/l - Secondary Oxygen
sbeox1v - Secondary Oxygen Raw
scan - scan
sigma-t00 - Density
sigma-t11 - Secondary Density
sigt - Density
temp - Temperature
wetcdom - CDOM Fluorescence
wet - CDOM Fluorescence
depsm - Depth
tv290c - Temperature
"""

def createDeckDF():
    deck = [

        ['SBE-9 Plus', '1145', ['scan', 'Pressure', 'Temperature', 'Conductivity', 'Salinity', 'Density', 'Oxygen Saturation', 'Fluorescence']],
        ['SBE-911', '1221', ['scan', 'Pressure', 'Temperature', 'Conductivity', 'Salinity', 'Density', 'Oxygen Saturation', 'Fluorescence', 'Irradiance', 'pH', 'Transmissometer transmission', 'Transmissometer attenuation', 'CDOM Fluorescence']],
        ['XBT', '1098', ['scan', 'Pressure', 'Temperature', 'Conductivity', 'Salinity', 'Density', 'Oxygen Saturation', 'Fluorescence']],
        ['SBE-911', ' S1460', ['scan', 'Pressure', 'Temperature', 'Conductivity', 'Salinity', 'Density', 'Oxygen Saturation', 'Fluorescence', 'Irradiance', 'pH', 'Transmissometer transmission', 'Transmissometer attenuation', 'CDOM Fluorescence']],
        ['SBE-911', ' XXXX', ['scan', 'Pressure', 'Temperature', 'Conductivity', 'Salinity', 'Density', 'Oxygen Saturation', 'Fluorescence', 'Irradiance', 'pH', 'Transmissometer transmission', 'Transmissometer attenuation', 'CDOM Fluorescence']]
        
    ]

    deck_df = pd.DataFrame.from_records(deck)
    return deck_df

###########################################################################################################

def dropByStandardizedList(cast, df, list=["scan", "Pressure","Temperature", "Salinity"]):
    # makes call to convert df to Standardized names
    dropped_df = cnv_tk.StandardizedDF(cast, df)
    for c in dropped_df:
        if c in list:
            continue
        else:
            dropped_df = dropped_df.drop([c], axis=1)

    cnv_tk.fixColumnNames(cast, dropped_df)
    return dropped_df

###########################################################################################################

def dropAny(cast, df, list=["scan", "Pressure", "Temperature", "Salinity"]):
    dropped_df = df.copy()
    for c in dropped_df:
        if c in list:
            continue
        else:
            dropped_df = dropped_df.drop([c], axis=1)

    cnv_tk.fixColumnNames(cast, dropped_df)
    return dropped_df

###########################################################################################################

def dropColumns(cast, df, deck=createDeckDF()):
    # TODO create temp df with Standardized names, check for data index to drop, store names of index in list,
    #  drop original cols by name this way we can retain original naming scheme if needed

    # list of columns to keep
    toKeep = []
    df = cnv_tk.StandardizedDF(cast, df)
    dropped_df = df.copy()

    match = False
    for d in deck.values:
        if cast.Instrument == d[1]:
            toKeep = d[2]
            match = True
            break
        else:
            continue

    if not match:
        print("No Matching Serial Number!\nUsing Default: 'scan', 'Pressure', 'Depth', 'Temperature', 'Salinity', 'Density'")
        toKeep = ['scan', 'Pressure', 'Depth', 'Temperature', 'Salinity', 'Density']

    for c in dropped_df:
        if c in toKeep:
            #dropped_df[c] = df[c]
            continue
        else:
            dropped_df = dropped_df.drop([c], axis=1)

    cnv_tk.fixColumnNames(cast, dropped_df)
    return dropped_df

###########################################################################################################

if __name__ == '__main__':
    df = createDeckDF()
