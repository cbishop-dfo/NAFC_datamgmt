exec(open("C:\QA_paths\set_QA_paths.py").read())

from Toolkits import cnv_tk
from Toolkits import ships_biological
import os
import csv
from tkinter.filedialog import askopenfile
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

# Bottle = Master
# Biomass = Joiner
def MacthID( Bottle, Biomass):
    fileCount = 0
    totalFileCount = Biomass.shape[0]
    lastPerc = 0
    perc = 0
    ID_List = []
    # Ship trip station id's (unique)
    UID = []
    BottleIDs = []
    try:
        for bio in Biomass.values:
            perc = int(fileCount/totalFileCount*100)
            if perc > lastPerc:
                print(str(perc) + " %")
                lastPerc = perc
            fileCount = fileCount + 1
            id = None
            b_id = None
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
                        tempCast.shipName = ""
                        tempCast.ship = ""
                        tempCast.trip = ""
                        for c in shipTrip:
                            if not c.isdigit():
                                tempCast.ShipName = tempCast.ShipName + str(c).lower()
                            else:
                                tempCast.trip = tempCast.trip + str(c)
                        ships_biological.getShipNumber(tempCast)
                        id = str(tempCast.ship) + str(tempCast.trip)
                        # TODO: Investigate UID
                        uid = bot[2]
                        # Matching Latitudes
                        if bot[6] == bio[3]:
                            # Matching Longitudes
                            if bot[7] == bio[4]:
                                # Matching dates

                                # Formatting bio datetime
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
                max_index = tempBotIDs.index(max(tempBotIDs))
                b_id = tempBotIDs[max_index][1]

            ID_List.append(id)
            UID.append(uid)
            BottleIDs.append(b_id)
    except Exception as e:
        print("ERROR: " + e.__str__())
    print(Biomass.shape[0])
    print(ID_List.__len__())
    Biomass["NewShipTrip"] = ID_List
    Biomass["UID"] = UID
    Biomass["NewSampleID"] = BottleIDs
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

   # newdf = pd.merge(Joiner, Master, how="left", right_on=["Latitude", "Longitude", "Date", "GMT", "Section", "Station"], left_on=["Lat", "Lon", "Date", "TimeUTC", "Section", "Station"])
   # newdf["SampleID"] = newdf["ID"]
#
   # newdf.to_sql('BIO', con=engine)
   # Master.to_sql('Master', con=engine)
   # Joiner.to_sql('Joiner', con=engine)
#
   # # query = """
   # # UPDATE BIO
   # # SET SampleID = ID
   # # WHERE JDate = MDate
   # # """
#
#
#
   # query = """
   #     Select ID
   #     From Master
   #     Left Join Joiner on Joiner.SampleID = ID
   #     Where Master.Date = Joiner.Date
   #     """
#
   # #query2 = """
   # #        Select SampleID
   # #        From Joiner
   # #        Left Join Master on Joiner.SampleID = Master.ID
   # #        Where Master.Date = Joiner.Date
   # #        """
   # engine.execute(query)
   # #engine.execute(query2)
   # #engine.execute("Set Joiner.SampleID = Master.ID where "
   # #               "Joiner.Latitude = Master.Lat AND"
   # #               " Joiner.Longitude = Master.Lon AND"
   # #               " Joiner.Date = Master.Date AND"
   # #               " Joiner.GMT = Master.TimeUTC"
   # #               " AND Joiner.Section = Master.Section AND"
   # #               " Joiner.Station = Master.Station")
#
   # #engine.execute("Select ID From Master,Joiner where "
   # #               "Joiner.Latitude = Master.Lat AND"
   # #               " Joiner.Longitude = Master.Lon AND"
   # #               " Joiner.Date = Master.Date AND"
   # #               " Joiner.GMT = Master.TimeUTC"
   # #               " AND Joiner.Section = Master.Section AND"
   # #               " Joiner.Station = Master.Station")
#
   # rows = engine.execute("SELECT * FROM Joiner").fetchall()
   # row = engine.execute("SELECT * FROM Master").fetchall()
   # slDF = pd.read_sql_table("Joiner", engine)
   # s2DF = pd.read_sql_table("Master", engine)
   # newdf = newdf[newdf['ShipTrip'].notna()]
   # for n in range(24):
   #     i = len(newdf.columns)-1
   #     newdf = newdf.drop(newdf.columns[i], axis=1)
   # newdf = newdf.drop_duplicates()
   # newdf = newdf.drop_duplicates(subset=['SampleID'])
   # filename = input("Enter name for file: ")
   # newdf.to_excel(filename, index=False)
#
   # print()
