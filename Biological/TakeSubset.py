#exec(open("C:\QA_paths\set_QA_paths.py").read())

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
def ReadPlank(f):
    plankArr = []
    for line in f:
        ship = line[1:7]
        #trip = line[4:7]
        station = line[8:10]
        year = line[10:12]
        day = line[12:15]
        botDepth = line[16:19]
        lat = line[19:24]
        lon = line[24:29]
        nav = line[30:31]
        gear = line[38:40]
        mesh = line[40:43]
        watvol = line[44:49]
        stime = line[49:53]
        etime = line[53:57]
        minDepth = line[58:61]
        maxDepth = line[62:65]
        pvol = line[66:69]
        pwt = line[70:74]
        gstat = line[75:77]
        sampstat = line[76:78]
        sampqual = line[78:79]
        towdur = line[80:84]
        convfact = line[85:90]
        subsamp = line[91:92]
        preserv = line[92:93]
        species = line[93:99]
        stage = line[99:102]
        state = line[103:104]
        measure = line[105:106]
        size = line[109:112]
        number = line[113:118]
        specnum = line[120:130]

        row = [ship.__str__(), station, year, day, botDepth, lat, lon, nav, gear, mesh, watvol,
               stime, etime, minDepth, maxDepth, pvol, pwt, gstat, sampstat, sampqual, towdur, convfact,
               subsamp, preserv, species, stage, state, measure, size, number, specnum]

        plankArr.append(row)

    cols = ["ship", "stn", "year", "day", "bdep", "lat", "long", "nav", "gear", "mesh",
            "watvol", "stime", "etime", "mindep", "maxdep", "pvol", "pwt", "gearstat",
            "sampstat", "sampqual", "towdur", "convfac", "subsamp", "preserv", "species",
            "stage", "state", "measure", "size", "number", "specnum"]
    return pd.DataFrame(plankArr, columns=cols)

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    engine = create_engine('sqlite://', echo=False)

    print("Select AZMP_Bottle File")
    file1 = askopenfile().name
    print("Select Biomass File")
    file2 = askopenfile().name
    print("Select Plank File")
    file3 = askopenfile().name

    f = open(file3)
    #arr = ReadPlank(f)

    azmp = pd.read_excel(file1, header=1)
    biomass = pd.read_excel(file2)
    #f = open(file3, "r")
    plank = ReadPlank(f)
    plank = pd.DataFrame(plank)
    #plank = pd.read_csv(file3, sep="\t", header=None)
    ship = input("Enter Ship Number: ")
    trip = input("Enter Trip Number: ")
    station = input("Enter Station Number: ")

    subset = ship + trip + station
    # Default shipname
    shipname = "xxx"

    cast = cnv_tk.Cast()
    cast.ship = ship
    ships_biological.getShipName(cast)
    shipname = cast.ShipName.upper()

    azmp_sub = azmp[azmp["Ship_Trip"] == int(ship.__str__() + trip.__str__())]
    biomass_sub = biomass[biomass["ShipTrip"] == shipname + trip.__str__()]
    plank_sub = plank[plank["ship"] == shipname + trip.__str__()]
    print()
    azmp_sub.to_excel(shipname + trip.__str__() + "_azmp" + ".xlsx", index=False)
    biomass_sub.to_excel(shipname + trip.__str__() + "_biomass" + ".xlsx", index=False)
    plank_sub.to_excel(shipname + trip.__str__() + "_plank" + ".xlsx", index=False)