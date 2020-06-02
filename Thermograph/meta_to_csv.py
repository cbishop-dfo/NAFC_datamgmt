import csv
import os

""" 
reads meta data from Deployments table of the thermo.db file and writes it to a csv file.
Csv file name is based on running directory.
created by Dylan Kennedy, 2019-06-17

TODO: add a method to change database path, as "thermo.db" needs to be in running directory.

"""

def writeMeta(datafile, filename):
    try:
        f = open(datafile, "r")
    except:
        exit()

    f.readline()
    read = 'true'
    for i in range(13):
        line = f.readline()
        line.replace('null', "")

        if line.__contains__('STATION'):
            SiteCode = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('SITE_NAME'):
            SiteName = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('LATITUDE'):
            Latitude = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('LONGITUDE'):
            Longitude = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('START_DATE'):
            DeploymentDate = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('START_TIME'):
            DeploymentTime = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('END_DATE'):
            RecoveredDate = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('END_TIME'):
            TimeOfRecovery = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('SAMPLING_INTERVAL'):
            SamplingSize = line.split('=')[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_DEPTH'):
            DeploymentDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('WATER_DEPTH'):
            DeploymentSiteDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('FILE_NAME'):
            datafile = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_TYPE'):
            InstrumentType = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                 "").rstrip()

        elif line.__contains__('SERIAL_NUMBER'):
            InstrumentNum = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                "").rstrip()
    row = [SiteCode, SiteName, Latitude, Longitude, DeploymentSiteDepth, DeploymentDepth, DeploymentDate, DeploymentTime
        , RecoveredDate, TimeOfRecovery, SamplingSize, InstrumentNum, InstrumentType, dir_path + "\\" +datafile ]

    print(row[6])
    with open(filename, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

    csvFile.close()


def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        if entry.endswith('.rpf'):
            allFiles.append(entry)
    return allFiles

def TitleNames():
    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)


    filename = pathname[pathname.__len__() - 1] + ".csv"

    if hasNumbers(filename):
        filename = pathname[pathname.__len__() - 2] + "_" + pathname[pathname.__len__() - 1] + ".csv"

    toprow = ['SiteCode', 'SiteName', 'Latitude', 'Longitude', 'DeploymentSiteDepth', 'DeploymentDepth', 'DeploymentDate', 'DeploymentTime'
        , 'RecoveredDate', 'TimeOfRecovery', 'SamplingSize', 'InstrumentNum', 'InstrumentType', 'Path']

    with open(filename, 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(toprow)

    csvFile.close()

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    dir_path = os.path.dirname(os.path.realpath(__file__))
    pathname = dir_path.replace("\\", '/').split('/')

    TitleNames()


    SiteCode = ""
    SiteName = ""
    Latitude = ""
    Longitude = ""
    DeploymentDate = ""
    DeploymentTime = ""
    RecoveredDate = ""
    TimeOfRecovery = ""
    SamplingSize = ""
    DeploymentDepth = ""
    DeploymentSiteDepth = ""
    InstrumentType = ""
    InstrumentNum = ""

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)

    filename = pathname[pathname.__len__() - 1] + ".csv"

    if hasNumbers(filename):
        filename = pathname[pathname.__len__() - 2] + "_" + pathname[pathname.__len__() - 1] + ".csv"

    files = getListOfFiles(dirName)
    for f in files:
        datafile = f
        writeMeta(datafile, filename)

    print("******************************")
