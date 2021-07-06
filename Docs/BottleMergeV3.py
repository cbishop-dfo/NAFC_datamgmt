exec(open("C:\QA_paths\set_QA_paths.py").read())

from Toolkits import cnv_tk
from Toolkits import ships_biological
import os
import csv
from tkinter.filedialog import askopenfile
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
"""
BottleMergeV3
-------------

Script merges AZMP and Bottle files together.
User is prompted to select the AZMP file and the Biomass file

"""


# Bottle = Master
# Biomass = Joiner
def MacthID(Bottle, Biomass):
    """
    :param Bottle: Pandas dataframe of the AZMP csv
    :param Biomass: Pandas dataframe of the Biomass csv
    :return: writes merged dataframes to NEWBIOMASS.csv
    """
    fileCount = 0
    totalFileCount = Biomass.shape[0]
    lastPerc = 0
    perc = 0
    ID_List = []
    # Ship trip station id's (unique)
    UID = []
    bottomBottleIDs = []
    topBottleIDs = []
    try:
        for bio in Biomass.values:
            perc = int(fileCount/totalFileCount*100)
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
            try:
                # Matching Biomass shiptrip id's to bottle file
                for bot in Bottle.values:
                    # Macthing shipTrip
                    if bot[1] == bio[0]:
                        tempCast = cnv_tk.Cast()
                        shipTrip = bot[1]
                        tempCast.ShipName = ""
                        tempCast.ship = ""
                        tempCast.trip = ""
                        tempCast.station = ""

                        for c in shipTrip:
                            if not c.isdigit():
                                tempCast.ShipName = tempCast.ShipName + str(c).lower()
                            else:
                                tempCast.trip = tempCast.trip + str(c)
                        ships_biological.getShipNumber(tempCast)
                        id = str(tempCast.ship) + str(tempCast.trip)
                        try:
                            tempCast.station = bio[2].split("-")[1]
                        except:
                            tempCast.station = bio[2].split(" Set ")[1]

                        if tempCast.station.__len__() == 1:
                            tempCast.station = "00" + tempCast.station

                        elif tempCast.station.__len__() == 2:
                            tempCast.station = "0" + tempCast.station
                        # TODO: Investigate UID, UID is shiptripstation
                        uid = str(tempCast.ship) + str(tempCast.trip) + str(tempCast.station)
                        # Matching Latitudes
                        botLat = "{:.2f}".format(bot[6])
                        biolat = "{:.2f}".format(bio[3])
                        if botLat == biolat:
                            # Matching Longitudes
                            botLon = "{:.2f}".format(bot[7])
                            biolon = "{:.2f}".format(bio[4])
                            if botLon == biolon:
                                # Matching dates

                                # Formatting bio datetime
                                try:
                                    datetime = bio[5].split("T")[0].split("-")
                                except:
                                    datetime = bio[5].split("-")
                                day = datetime[2]
                                month = datetime[1]
                                year = datetime[0]
                                biodate = day + "/" + month + "/" + year

                                # Formatting bot datetime
                                datetime = bot[8].split("/")
                                day = datetime[0]
                                month = datetime[1]
                                year = datetime[2]
                                if day.__len__() < 2:
                                    day = "0" + day
                                if month.__len__() < 2:
                                    month = "0" + month
                                botdate = day + "/" + month + "/" + year
                                if botdate == biodate:
                                    # pres = bot[10]
                                    tempBotIDs.append([bot[10], bot[0]])
            except Exception as e:
                print(e.__str__())
            if tempBotIDs.__len__() > 0:
                # Bottom depth id
                max_index = tempBotIDs.index(max(tempBotIDs))
                b_id = tempBotIDs[max_index][1]
                # 5m bottle id
                min_index = tempBotIDs.index(min(tempBotIDs))
                t_id = tempBotIDs[min_index][1]

            ID_List.append(id)
            UID.append(uid)
            bottomBottleIDs.append(b_id)
            topBottleIDs.append(t_id)
    except Exception as e:
        print("ERROR: " + e.__str__())
    print(Biomass.shape[0])
    print(ID_List.__len__())
    Biomass["NewShipTrip"] = ID_List
    Biomass["UID"] = UID
    Biomass["BottomSampleID"] = bottomBottleIDs
    Biomass["TopSampleID"] = topBottleIDs
    Biomass.to_csv("NEWBIOMASS.csv", index=False)
    print()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    engine = create_engine('sqlite://', echo=False)

    print("Select NEW_AZMP_Bottle File")
    file1 = askopenfile().name
    print("Select Biomass File")
    file2 = askopenfile().name
    Master = pd.read_csv(file1)

    Joiner = pd.read_excel(file2)
    Master["Date"] = Master["Date"].values.astype(str)
    Joiner["Date"] = Joiner["Date"].values.astype(str)
    Master["GMT"] = Master["GMT"].values.astype(str)
    Joiner["TimeUTC"] = Joiner["TimeUTC"].values.astype(str)

    masterDate = []
    joinerDate = []

    for d in Master["Date"].values:
        dat = d.split("T")[0]
        masterDate.append(dat)
    Master["Date"] = masterDate

    for d in Joiner["Date"].values:
        dat = d.split()[0]
        joinerDate.append(dat)
    Joiner["Date"] = joinerDate

    MacthID(Master, Joiner)
