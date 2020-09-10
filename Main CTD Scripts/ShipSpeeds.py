import os
from Toolkits import cnv_tk
from Toolkits import dir_tk
import pandas as pd
import datetime
from geopy import distance

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


def CreateDistanceArray(df):
    lastPoint = -999
    currentPoint = -999
    distances = []
    for d in df.values:

        if lastPoint == -999:
            lastPoint = d[2].__str__() + " " + d[3].__str__()
            distances.append(0)
        else:
            currentPoint = d[2].__str__() + " " + d[3].__str__()
            result = distance.distance(lastPoint, currentPoint).kilometers
            distances.append(result)
            lastPoint = currentPoint

    return distances



###########################################################################################################
# Calculate speed in km/h
def CreateSpeedArray(df):
    lastTime = -999
    currentTime = -999
    speeds = []
    deltat = []
    deltatime = ""

    for d in df.values:
        try:

            if lastTime == -999:
                date = d[1]
                lastTime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                speeds.append(0)
                deltat.append(0)
            else:
                date = d[1]
                try:
                    currentTime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print("\nERROR with Station: " + d[0] + " Date: " + date + "\n" + e.__str__() +
                          "\nAttempting to fix datetime...")
                    fixdate = d[1] + ":00"
                    currentTime = datetime.datetime.strptime(fixdate, '%Y-%m-%d %H:%M:%S')
                    print("\nDatetime changed from " + date + " to " + fixdate + "\n")


                time_delta = (currentTime - lastTime)
                total_seconds = time_delta.total_seconds()
                speed = d[4]/(total_seconds/3600)
                speeds.append(speed*0.539957)
                deltat.append(total_seconds)
                lastTime = currentTime
        except Exception as e:
            print(e.__str__())

    print("Speeds: ")
    for s in speeds:
        print(s)
    return [speeds, deltat]

###########################################################################################################

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    # Creating dictionary to store each files specified data to later convert to pandas Dataframe
    Dictionary = createDict()

    files = dir_tk.getListOfFiles(dirName)
    lastPoint = ""
    currentPoint = ""
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
    distanceArray = CreateDistanceArray(df)
    df["Distance (km)"] = distanceArray
    speedArray = CreateSpeedArray(df)
    df["Speeds (Knots)"] = speedArray[0]
    df["Delta Time(seconds)"] = speedArray[1]
    df.to_csv("ShipSpeeds.csv")

    # Any additional code you wish to write using the dataframe can go HERE:

    print("Complete!")
