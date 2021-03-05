exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import dir_tk
import os
import csv

def writeIDENT(csvList):

    with open(csvName, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["ship", "stn", "year", "day", "bdep", "lat", "long", "nav", "gear", "mesh",
                         "watvol", "stime", "etime", "mindep", "maxdep", "pvol", "pwt", "gearstat",
                         "sampstat", "sampqual", "towdur", "convfac", "subsamp", "preserv", "species",
                         "stage", "state", "measure", "size", "number", "specnum"])
        for row in csvList:
            writer.writerow(row)

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

        if datafile.lower().endswith(".ident"):

            f = open(datafile, "r")
            csvName = "PLANK_SORT.csv"
            csvList = []
            for line in f:
                ship = line[1:4]
                trip = line[4:7]
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

                row = [ship.__str__() + trip.__str__(), station, year, day, botDepth, lat, lon, nav, gear, mesh,watvol,
                       stime, etime, minDepth, maxDepth, pvol, pwt, gstat, sampstat, sampqual, towdur, convfact,
                       subsamp,preserv, species, stage, state, measure, size, number, specnum]

                csvList.append(row)

            writeIDENT(csvList)
            print("Complete")
