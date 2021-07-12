exec(open("C:\QA_paths\set_QA_paths.py").read())

from Toolkits import cnv_tk
from Toolkits import ships_biological
import os
import csv
from tkinter.filedialog import askopenfile
import pandas as pd
import sqlite3
from sqlalchemy import create_engine


def MacthID(Plank):
    fileCount = 0
    totalFileCount = Plank.shape[0]
    lastPerc = 0
    perc = 0
    ID_List = []
    # Ship trip station id's (unique)
    UID = []
    bottomBottleIDs = []
    topBottleIDs = []
    for plk in Plank.values:
        perc = int(fileCount / totalFileCount * 100)
        if perc > lastPerc:
            print(str(perc) + " %")
            lastPerc = perc
        fileCount = fileCount + 1
        id = None
        b_id = None
        t_id = None
        uid = None
        shipTripStation = None
        tempBotIDs = []
        # Macthing shipTrip


        tempCast = cnv_tk.Cast()
        shipTrip = plk[0]
        tempCast.ShipName = ""
        tempCast.ship = "00"
        tempCast.trip = ""
        tempCast.station = "xxx"
        for c in shipTrip:
            if not c.isdigit():
                tempCast.ShipName = tempCast.ShipName + str(c).lower()
            else:
                tempCast.trip = tempCast.trip + str(c)
        ships_biological.getShipNumber(tempCast)
        id = str(tempCast.ship) + str(tempCast.trip)

        tempCast.station = plk[1].__str__()

        if tempCast.station.__len__() == 1:
            tempCast.station = "00" + tempCast.station
        elif tempCast.station.__len__() == 2:
            tempCast.station = "0" + tempCast.station
        # TODO: Investigate UID, UID is shiptripstation
        uid = str(tempCast.ship) + str(tempCast.trip) + str(tempCast.station)
        ID_List.append(id)
        UID.append(uid)

    Plank["ShipTrip"] = ID_List
    Plank["ShipTripStation"] = UID
    Plank.to_csv("new_plank.csv", index=False)
    print()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    engine = create_engine('sqlite://', echo=False)

    print("Select Plank File")
    file1 = askopenfile().name
    Plank = pd.read_csv(file1)

    MacthID(Plank)
