import os
import datetime

__author__ = 'KennedyDyl'

'''
***************************************************************
Reads through .rpf files in current directory and filters out files with inconsistent sample sizes.
created by Dylan Kennedy, 2019-07-05

Script checks if the sample size is equal to 1 hour, if true the file gets written to ValidSampleSize.
If false, file is instead written to InvalidSampleSize.

Creates two subfolders in current directory:
  
  [1] - ValidSampleSize 
  [2] - InvalidSampleSize


***************************************************************    
'''


class Deployments(object):

    def __init__(self, datafile=None):
        self.datafile = datafile
        self.initialize_vars()

    def initialize_vars(self):
        self.id = "null"
        self.InstrumentType = "null"
        self.SiteName = "null"
        self.SiteCode = "null"
        self.InstrumentNum = "null"
        self.Latitude = "null"
        self.Longitude = "null"
        self.DeploymentDepth = "null"
        self.DeploymentDate = "null"
        self.DeploymentTime = "null"
        self.RecoveredDate = "null"
        self.TimeOfRecovery = "null"
        self.SamplingSize = "null"
        self.DeploymentSiteDepth = "null"
        self.data = []
        self.directory = 'thermo.db'  # DB Location.
        self.datafile = ""

        self.Fix = []


###########################################################################################################


def getFilename(datafile):
    path = datafile.replace("\\", "/").split("/")
    return path[path.__len__() - 1]


###########################################################################################################


# Reads .rpf file and creates deployment object.
def read_rpf(datafile):
    print("Processing " + datafile)
    data = Deployments(datafile)
    data.datafile = getFilename(datafile)
    try:
        f = open(datafile, "r")
    except:
        exit()

    f.readline()
    isdata = 'false'
    for line in f:

        if line.replace("\n", "").__contains__(
                '-- DATA --'):  # Data and format were inconsistent, needed to check each line in header
            isdata = 'true'
            break

        elif line.__contains__('STATION'):
            data.SiteCode = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('SITE_NAME'):
            data.SiteName = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('LATITUDE'):
            data.Latitude = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('LONGITUDE'):
            data.Longitude = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('START_DATE'):
            data.DeploymentDate = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('START_TIME'):
            data.DeploymentTime = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('END_DATE'):
            data.RecoveredDate = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('END_TIME'):
            data.TimeOfRecovery = line.strip().split('=')[1].replace(",", "").replace("\n", "")

        elif line.__contains__('SAMPLING_INTERVAL'):
            data.SamplingSize = line.split('=')[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('WATER_DEPTH'):
            data.DeploymentSiteDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_DEPTH'):
            data.DeploymentDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('FILE_NAME'):
            data.datafile = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_TYPE'):
            data.InstrumentType = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                 "").rstrip()

        elif line.__contains__('SERIAL_NUMBER'):
            data.InstrumentNum = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                "").rstrip()

    if isdata == 'true':
        for lin in f:
            l = lin.split()
            data.data.append(l)
            dataDate = l[0].replace("'", "")
            dataTime = l[1].replace("'", "").replace(".", ":")
            dataTemp = l[2].replace("'", "")

        return data


###########################################################################################################

# Adds Data to be removed (from main array) into trimmed data, consists of data between the specified points.
def trim_data(data):
    for d in data.data:
        for t in data.Trim:
            try:
                if int(d[3]) >= int(t[0]) and int(d[3]) <= int(t[1]):
                    data.TrimmedData.append(d)
            except:
                print("ERROR: TYPE_NONE")



###########################################################################################################


# Removes Trimmed data from main array
def getFinal(deployment):
    deployment.finaldata = deployment.data
    for t in deployment.TrimmedData:
        try:
            deployment.finaldata.remove(t)
        except:
            continue


###########################################################################################################

def writeData(data):
    f = open(datafile,
             "w+")
    f.write(
        "HEADER,\n" +
        "   STATION=" + data.SiteCode + "," + "\n" +
        "   SITE_NAME=" + data.SiteName + "," + "\n" +
        "   START_DATE=" + data.DeploymentDate.replace("/", "-") + "," + "\n" +
        "   START_TIME=" + data.DeploymentTime + "," + "\n" +
        "   END_DATE=" + data.RecoveredDate.replace("/", "-") + "," + "\n" +
        "   END_TIME=" + data.TimeOfRecovery + "," + "\n" +
        "   LATITUDE=" + data.Latitude + "," + "\n" +
        "   LONGITUDE=" + data.Longitude + "," + "\n" +
        "   INST_TYPE=" + data.InstrumentType + "," + "\n" +
        "   SERIAL_NUMBER=" + data.InstrumentNum + "," + "\n" +
        "   WATER_DEPTH=" + data.DeploymentSiteDepth + "," + "\n" +
        "   INST_DEPTH=" + data.DeploymentDepth + "," + "\n" +
        "   SAMPLING_INTERVAL=" + data.SamplingSize + "," + "\n" +
        "   FILE_NAME=" + data.datafile + "," + "\n" + "-- DATA --\n")

    for d in data.data:
        try:
            check = d[1].split(":")
            cLen = check.__len__()
            if cLen > 3:
                check = check[0] + ":" + check[1] + ":" + check[2]
                _datetime = d[0] + " " + check.replace(".", ":")
                _temp = float(d[2])

            else:
                _datetime = d[0] + " " + d[1].replace(".", ":")
                _temp = float(d[2])

            f.write(_datetime + " " + _temp.__str__() + "\n")
        except:
            print("Error writing data")
            input("press enter to continue...")
            continue

###########################################################################################################


# Writes meta data and thermo data into new trimmed .rpf file.
def sample_rpf(data):
    currentSample = 0
    lastSample = 0

    # Checks each entry in dataframe for time of 1 hour
    for dat in data.data:
        data.Fix.append(dat)
        try:
            date = dat[0] + " " + dat[1]
            lastSample = currentSample
            currentSample = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

            if(lastSample != 0):

                dif = abs(currentSample - lastSample)
                if dif.seconds != 3600:
                    createInvalidFolder()
                    writeData(data)
                    break

                elif dif.seconds == 3600:
                    createValidFolder()
                    writeData(data)
                    break
        except Exception as e:
            date = dat[0] + " " + dat[1]
            print(e)

###########################################################################################################


# If no subfolder called ValidSampleSize exists, creates new sub folder named ValidSampleSize to write files to.
def createValidFolder():
    current_path = os.path.dirname(os.path.realpath(__file__))

    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\ValidSampleSize\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)

###########################################################################################################


# If no subfolder called BadSampleSize exists, creates new sub folder BadSampleSize to write files to.
def createInvalidFolder():
    current_path = os.path.dirname(os.path.realpath(__file__))

    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\InvalidSampleSize\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)


###########################################################################################################


# Gets all files located in the dir of the running script.
def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        allFiles.append(entry)
    return allFiles


###########################################################################################################


if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = getListOfFiles(dirName)
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".rpf"):
            deployment = read_rpf(datafile)
            sample_rpf(deployment)

        else:
            print("File Not Supported...")

    print("******************************")
