import os
from Toolkits import cnv_tk
from Toolkits import dir_tk
import pandas as pd
from Toolkits import db_tk

# Creates dictionary to be used on each file in directory
def createDict():

    Dictionary = {}
    # Here is the data we wish to store
    allColumns = ["Station", "Date", "Latitude", "Longitude"]
    for c in allColumns:
        Dictionary[c] = []
    return Dictionary

###########################################################################################################


def PopulateDict(cast, Dictionary):

    # Here we assign specified variables into the dictionary (See: 'allColumns' Variable List Above In 'createDict()')
    Dictionary["Station"].append(cast.station)
    Dictionary["Date"].append(cast.CastDatetime)
    Dictionary["Latitude"].append(cast.Latitude)
    Dictionary["Longitude"].append(cast.Longitude)

###########################################################################################################


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    # Creating dictionary to store each files specified data to later convert to pandas Dataframe
    Dictionary = createDict()

    files = dir_tk.getListOfFiles(dirName)
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            PopulateDict(cast, Dictionary)

    # Creating pandas dataframe from dictionary containing info from all files
    df = pd.DataFrame.from_dict(Dictionary)

    # Any additional code you wish to write using the dataframe can go HERE:
    print("Complete!")