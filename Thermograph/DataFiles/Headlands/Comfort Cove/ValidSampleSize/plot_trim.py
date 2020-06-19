import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import interactive
import numpy as np

__author__ = 'KennedyDyl'

'''
Script to read in thermograph files(.rpf), trim them and write them back out as well as save trimmed plot.
created by Dylan Kennedy, 2019-06-17

Script takes all files in the current directory and searches for the .rpf files.
rpf files are read into the Deployment class and opens a trimming plot.

***************************************************************
    List of Instructions/Key Codes For Trimmer:
***************************************************************
    
    1) Mouse down selects start point for trimming, mouse up selects endpoint. To trim a region hold 
    left click on beginning of bad data and drag to end of bad data then release click. repeat for all bad data in plot.
    
    2) Enter or space: Confirm selection, trim data from deployment, write to file, save plot as png and close plot.
    
    3) q: quits trimming and closes plot
    
    4) r: redraws and updates plot
    
    5) p: Confirm selection, trim data from deployment, write to file but keeps plot open (mostly used for debugging).
    
    6) d: Gets standard deviation and trims all points outside of specified deviation.  
    
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
        self.directory = 'current.db'  # DB Location.
        self.datafile = ""

        self.startpoint = 0
        self.endpoint = 0
        self.Trim = []
        self.TrimmedData = []
        self.finaldata = []
        self.isTrimming = 'true'

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

        elif line.__contains__('INST_DEPTH'):
            data.DeploymentDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('WATER_DEPTH'):
            data.DeploymentSiteDepth = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('FILE_NAME'):
            data.datafile = line.split("=")[1].replace(",", "").replace("\n", "").replace(" ", "")

        elif line.__contains__('INST_TYPE'):
            data.InstrumentType = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                 "").rstrip()

        elif line.__contains__('SERIAL_NUMBER'):
            data.InstrumentNum = line.split("=")[1].replace(",", "").replace("\n", "").replace("'", "").replace(" ",
                                                                                                                "").rstrip()

    if isdata == 'true':
        count = 0
        for lin in f:
            l = lin.split()
            l.append(count)
            data.data.append(l)
            dataDate = l[0].replace("'", "")
            dataTime = l[1].replace("'", "").replace(".", ":")
            dataTemp = l[2].replace("'", "")
            count = count + 1

        return data


###########################################################################################################

# Adds Data to be removed (from main array) into trimmed data, consists of data between the specified points.
def trim_data(data):

    for d in data.data:
        for t in data.Trim:
            try:
                if int(d[3]) >= int(t[0]) and int(d[3])<= int(t[1]):
                    data.TrimmedData.append(d)
            except:
                print("ERROR: TYPE_NONE")

###########################################################################################################


# Mouse Listener for mouse down event.
def onclick(event, deployment):
    deployment.startpoint = event.xdata

###########################################################################################################


# Mouse Listener for mouse up event.
def onrelease(event, deployment, ax):
    deployment.endpoint = event.xdata
    t = [deployment.startpoint, deployment.endpoint]
    deployment.Trim.append(t)
    executeTrim(deployment)
    updatePlot(deployment, ax)

###########################################################################################################


# Key Listener for key down event.
def onkey(event, deployment, ax):

    # Closes plot without saving.
    if event.key == 'q':
        plt.close()
        deployment.isTrimming = 'false'
        interactive(False)

    # Used to redraw and update plot.
    if event.key == 'r':
        updatePlot(deployment, ax)

    # Confirm selection, trim data from deployment, write to file and close plot.
    if event.key == 'enter' or 'space':
        executeTrim(deployment)
        updatePlot(deployment, ax)
        getFinal(deployment)
        ax.figure.savefig(datafile.replace("_trimmed", "") + "_trimmed.png")
        write_rpf(deployment)
        plt.close()
        deployment.isTrimming = 'false'
        interactive(False)

    # Trims data from deployment but leaves plot open.
    if event.key == 'p':
        executeTrim(deployment)
        updatePlot(deployment, ax)
        getFinal(deployment)
        ax.figure.savefig(datafile.replace("_trimmed", "") + "_trimmed.png")
        write_rpf(deployment)

    # Gets standard deviation and trims all points outside of specified deviation.
    if event.key == 'd':
        getSD(deployment)
        updatePlot(deployment, ax)

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


# Writes meta data and thermo data into new trimmed .rpf file.
def write_rpf(data):
    f = open(datafile.replace("_trimmed.rpf", "").replace(".rpf", "") + "_trimmed.rpf",
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

    for dat in data.data:
        f.write(dat[0] + " " + dat[1] + " " + dat[2] + "\n")

###########################################################################################################


# If no subfolder called trimmed exists, creates new sub folder named trimmed to write new trimmed files to.
def createTrimmedFolder():
    current_path = os.path.dirname(os.path.realpath(__file__))

    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\trimmed\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)

###########################################################################################################


def executeTrim(deployment):
    trim_data(deployment)
    print("Trimmed")

###########################################################################################################

# Redraws plot and plots trimmed data.
def updatePlot(deployment, ax):
    plt.pause(.0001)

    ax.clear()
    for i in deployment.TrimmedData:
        Tyaxis.append(float(i[2]))
        Txaxis.append(float(i[3]))
    # plt.clear()
    ax.scatter(xaxis, yaxis, color='c', s=1)
    ax.scatter(Txaxis, Tyaxis, color='r', s=1)
    plt.pause(.0001)

###########################################################################################################


# Calculate Standard Deviation from data and removes any points outside specified deviation.
def getSD(deployment):
    x = np.mean(yaxis)
    std = np.std(yaxis)
    dv = float(input("Input Number of Deviations: "))
    thres = std*dv
    for k in deployment.data:
        if float(k[2]) > thres or float(k[2]) < -1*thres:
            deployment.TrimmedData.append(k)

###########################################################################################################


# Creates Plots/Figures/Buttons/Header for plot
def trim_rpf(deployment, xaxis, yaxis):

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.04, top=0.85, bottom=0.04, right=0.90)

    # plt.figure(1)
    ax.scatter(xaxis, yaxis, color='c', s=1)
    # ax.ion()


    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    mouseDown = fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, deployment))
    mouseUp = fig.canvas.mpl_connect('button_release_event', lambda event: onrelease(event, deployment, ax))
    keyDown = fig.canvas.mpl_connect('key_press_event', lambda event: onkey(event, deployment, ax))

    def reset(event):
        print("Trim Reset")
        deployment.Trim = []
        deployment.TrimmedData = []
        Txaxis.clear()
        Tyaxis.clear()
        updatePlot(deployment, ax)

    # Reset button, clears the trim points.
    resetax = plt.axes([.9, .8, 0.08, 0.04])
    button = Button(resetax, 'Reset')
    button.on_clicked(reset)

    # If recovered date is missing get date from data. (only a few files had this issue, was fixed later within the DB.)
    if deployment.RecoveredDate == 'null':
        estDateRocovered = deployment.data[deployment.data.__len__()-1][0]
        estTimeRecovered = deployment.data[deployment.data.__len__()-1][1]
        deployment.RecoveredDate = estDateRocovered
        deployment.TimeOfRecovery = estTimeRecovered

    # Header textbox, contains file information.
    hax = plt.axes([0.01, 0.99, 0.0, 0.0], facecolor='white')
    metatxt = datafile + "\n Start Date: " + deployment.DeploymentDate + "\n End Date: " + deployment.RecoveredDate + "\n OG_FILE: " + deployment.datafile
    props = dict(boxstyle='round', alpha=1)
    hax.text(0.05, 0.95, metatxt,  fontsize=14, verticalalignment='top', bbox=props)

    plt.show()

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
            createTrimmedFolder()

            # Global axis values for data plot and trimmed plot
            xaxis = []
            yaxis = []
            Txaxis = []
            Tyaxis = []

            # Creates x and y data for main plot.
            for i in deployment.data:
                yaxis.append(float(i[2]))
                xaxis.append(float(i[3]))

            # Call to create main plot and setup listeners.
            trim_rpf(deployment, xaxis, yaxis)

        else:
            print("File Not Supported...")

    print("******************************")
