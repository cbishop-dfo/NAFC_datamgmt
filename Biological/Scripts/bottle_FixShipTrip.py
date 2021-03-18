exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import dir_tk
from Toolkits import cnv_tk
from Toolkits import ships_biological
import os
import csv
import pandas as pd

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.confirmSelection(dirName)
    for f in files:
        # changes Dir back to original
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f

        if datafile.lower().endswith(".xlsx"):

            f = pd.read_excel(datafile, header=1)
            cast = cnv_tk.Cast()
            csvName = "NEW_AZMP.csv"
            #rows = f["Ship_Trip"].values
            FixedNames = []
            FixedDate = []
            Latitudes = []
            Longitudes = []
            Day = []
            Month = []
            Year = []

            for row in f.values:
                #row = row.__str__()
                shipNum = row[1].__str__()[0:2]
                trip = row[1].__str__()[2:]
                datetime = row[8]

                day = datetime.day.__str__()
                month = datetime.month.__str__()
                year = datetime.year.__str__()

                newdate = day + "/" + month + "/" + year
                tlat = row[6]
                tlon = row[7]
                lat = float("{0:.2f}".format(tlat))
                lon = float("{0:.2f}".format(tlon))
                if shipNum.isdigit():
                    cast.ship = shipNum
                    ships_biological.get_bio_ShipName(cast)
                    FixedNames.append(cast.ShipName.upper() + trip)
                else:
                    FixedNames.append(row)

                FixedDate.append(newdate)
                Latitudes.append(lat)
                Longitudes.append(lon)
                Day.append(day)
                Month.append(month)
                Year.append(year)

            f["Ship_Trip"] = FixedNames
            f["Date"] = FixedDate
            f["Latitude"] = Latitudes
            f["Longitude"] = Longitudes
            f["Day"] = Day
            f["Month"] = Month
            f["Year"] = Year
            f.to_csv(csvName, index=False)
            print("Complete")
