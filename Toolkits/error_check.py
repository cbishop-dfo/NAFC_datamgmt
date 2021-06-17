import pandas as pd
def checkdf(df, minRows=15):
    if len(df) < minRows:
        return False
    else:
        return True

def compairFilename(cast, datafile):
    uid = str(cast.ship) + str(cast.trip) + str(cast.station)
    #fileID = datafile.split("/")[-1].split(".")[0]

    fileID = datafile.split("/")[-1:]

    if str(uid) == str(fileID):
        print("ID" + uid)
        print("FileID" + fileID)
        return True
    else:
        print("ID" + uid)
        print("FileID" + fileID)
        return False

