import os
from Toolkits import dir_tk

###########################################################################################################

def getShipNumber(code):

    try:
        Ships = open("ships.txt")
    except:
        Ships = open("../Resources/ships.txt")

    for shipName in Ships:
        name = shipName.replace("\n", "").split()[2].lower()
        try:
            number = shipName.replace("\n", "").split()[0]
        except:
            continue
        if name == code:
            return number


###########################################################################################################

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.getListOfFiles(dirName)
    lastPoint = ""
    currentPoint = ""
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if not datafile.lower().__contains__("."):
            shipName = f.split("_")[0]
            shipCode = ''.join(i for i in shipName if not i.isdigit())
            shipNum = getShipNumber(shipCode)
            trip = shipName[shipCode.__len__():]
            set = f.split(".")[0].split("_")[2]
            year = f.split(".")[0].split("_")[1]
            newfile = shipNum.__str__() + trip.__str__() + set.__str__() + ".p" + year
            reader = open(f, "r")
            writer = open(newfile, "w+")
            for line in reader:
                writer.write(line)
            reader.close()
            writer.close()
