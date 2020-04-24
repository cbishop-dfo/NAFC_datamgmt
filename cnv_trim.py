import os
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import interactive
import numpy as np
import pandas as pd
import math
import cnv_tk
import matplotlib
from matplotlib.widgets import RectangleSelector
#matplotlib.use("qt4agg")

__author__ = 'KennedyDyl'

'''
Script to read in CTD files(.cnv), trim them and write them back out as well as save trimmed plot.
created by Dylan Kennedy, 2020-03-30

Script takes all files in the current directory and searches for the .cnv files.
cnv files are read into the Cast class from cnv_tk and opened for trimming.

***************************************************************
    List of Instructions/Key Codes For Trimmer:
***************************************************************

    1) Mouse down selects start point for trimming, mouse up selects endpoint. To trim a region hold 
    left click on beginning of bad data and drag to end of bad data then release click. repeat for all bad data in plot.

    2) Enter or space: Confirm selection, trim data from Cast, write to file, save plot as png and close plot.

    3) q: quits trimming and closes plot

    4) r: redraws and updates plot

    5) p: Confirm selection, trim data from Cast, write to file but keeps plot open (mostly used for debugging).

***************************************************************    

BUG FIXES NEEDED:

selection for trim points: can only select startpoint and endpoint once, these points are indexes in which data is removed.

imporved selection: can only select a trimpoint from clicking on point directly. Need to implement the rectangle select.


    



'''



###########################################################################################################

# Adds Data to be removed (from main array) into trimmed data, consists of data between the specified points.
def trim_data(data):
    for d in data.data:

         try:
            if d in data.Trim:
                 continue
            else:
                # append all data that is not in the Trim array.
                data.TrimmedData.append(d)
         except Exception as e:
             print(e)



###########################################################################################################


# Mouse Listener for mouse down event.
def onclick(event, cast):
    cast.startpoint = [event.xdata, event.ydata]
    print("index: " + event.ind.__str__())


###########################################################################################################


# Mouse Listener for mouse up event.
def onrelease(event, cast, ax):
    cast.endpoint = [event.xdata, event.ydata]
    print("index: " + event.ind.__str__())
    # TODO: implement 2d coord
    """
    if data depth > startdep && data depth < end dep
        if data temp > startemp && datatmp < end tmp 
    """
    #for i = cast.startpoint[0]
    for i in range(int(cast.startpoint[0]), int(cast.endpoint[0]),1):
        try:
            cast.Trim.append(cast.data[i])
        except Exception as e:
            print(e)
            continue
    #t = [cast.startpoint, cast.endpoint]
    #cast.Trim.append(t)
    executeTrim(cast)
    updatePlot(cast, ax)



###########################################################################################################

def onpick(event, cast, ax):
    ind = event.ind
    print("Point Selected")
    if cast.hasStart == False:
        cast.startpoint = ind
        cast.hasStart = True
    else:
        cast.endpoint = ind
        end = cast.endpoint[0]
        start = cast.startpoint[0]
        if end < start:
            temp = cast.endpoint
            cast.endpoint = cast.startpoint
            cast.startpoint = temp

        for i in range(int(cast.startpoint[0]), int(cast.endpoint[0]), 1):
            try:
                cast.Trim.append(cast.data[i])
            except Exception as e:
                print(e)
                continue
        # t = [cast.startpoint, cast.endpoint]
        # cast.Trim.append(t)
        cast.hasStart = False
        executeTrim(cast)
        updatePlot(cast, ax)


###########################################################################################################

def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    global x1, x2, y1, y2
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    #close()

def toggle_selector(event):
    print (' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print (' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print (' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)

###########################################################################################################

# Key Listener for key down event.
def onkey(event, cast, ax):
    # Closes plot without saving.
    if event.key == 'q':
        plt.close()
        cast.isTrimming = 'false'
        interactive(False)

    # Used to redraw and update plot.
    if event.key == 'r':
        updatePlot(cast, ax)

    # Confirm selection, trim data from deployment, write to file and close plot.
    if event.key == 'enter' or 'space':
        executeTrim(cast)
        updatePlot(cast, ax)
        getFinal(cast)
        ax.figure.savefig(datafile.replace("_trimmed", "") + "_trimmed.png")
        write_rpf(cast)
        plt.close()
        cast.isTrimming = 'false'
        interactive(False)

    # Trims data from deployment but leaves plot open.
    if event.key == 'p':
        executeTrim(cast)
        updatePlot(cast, ax)
        getFinal(cast)
        ax.figure.savefig(datafile.replace("_trimmed", "") + "_trimmed.png")
        write_rpf(cast)



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
    print(data.data.__len__())
    print(data.TrimmedData.__len__())

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


def executeTrim(cast):
    trim_data(cast)
    print("Trimmed")


###########################################################################################################

# Redraws plot and plots trimmed data.
def updatePlot(cast, ax):
    plt.pause(.0001)

    ax.clear()
    for i in cast.Trim:
        Txaxis.append(float(i[1]))
        Tyaxis.append(float(i[2]))
    # plt.clear()
    ax.scatter(cast.xaxis, cast.yaxis, color='c', s=5)
    ax.scatter(Txaxis, Tyaxis, color='r', s=5)
    plt.pause(.0001)


###########################################################################################################


# Creates Plots/Figures/Buttons/Header for plot
def trim_cast(cast, xaxis, yaxis):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.04, top=0.85, bottom=0.04, right=0.90)

    # plt.figure(1)
    ax.scatter(xaxis, yaxis, color='c', s=1, picker=True)
    #ax.ion()

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    #mouseDown = fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, cast))
    #mouseUp = fig.canvas.mpl_connect('button_release_event', lambda event: onrelease(event, cast, ax))
    #keyDown = fig.canvas.mpl_connect('key_press_event', lambda event: onkey(event, cast, ax))
    fig.canvas.mpl_connect('pick_event', lambda event: onpick(event, cast, ax))

    def reset(event):
        print("Trim Reset")
        cast.Trim = []
        cast.TrimmedData = []
        Txaxis.clear()
        Tyaxis.clear()
        cast.hasStart = False
        cast.startpoint = None
        cast.endpoint = None
        updatePlot(cast, ax)

    # Reset button, clears the trim points.
    resetax = plt.axes([.9, .8, 0.08, 0.04])
    button = Button(resetax, 'Reset')
    button.on_clicked(reset)

    # Header textbox, contains file information.
    hax = plt.axes([0.01, 0.99, 0.0, 0.0], facecolor='grey')
    metatxt = datafile + "\n Start Date: " + cast.CastDatetime + "\n" + " OG_FILE: " + cast.datafile
    props = dict(boxstyle='round', alpha=1)
    hax.text(0.05, 0.95, metatxt, fontsize=14, verticalalignment='top', bbox=props)
    toggle_selector.RS = RectangleSelector(ax, line_select_callback, drawtype='box', useblit=True,
                                           button=[1, 3], minspanx=5, minspany=5, spancoords='pixels')
    plt.connect('key_press_event', toggle_selector)
    plt.pause(.0001)
    plt.show()
    plt.pause(.0001)


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
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            createTrimmedFolder()
            df = cnv_tk.cnv_to_dataframe(cast)

            # Global axis values for data plot and trimmed plot
            cast.xaxis = df[cast.ColumnNames[1]].values.astype(float)
            cast.yaxis = df[cast.ColumnNames[2]].values.astype(float)
            Txaxis = []
            Tyaxis = []

            # Creates x and y data for main plot.

            #yaxis = df["prDM"].values
            #xaxis = df["t090C"].values

            #fig = px.scatter(df, x="t090C", y="prDM")
            #fig.show()

            #yaxis = [1,2,3,4,5]
            #xaxis = [1,2,3,4,5]

            #plt.scatter(xaxis, yaxis)
            #df.plot(kind='scatter', x='t090C', y='prDM', color='blue')
            #plt.show()


            # Call to create main plot and setup listeners.
            trim_cast(cast, cast.xaxis, cast.yaxis)

        else:
            print("File Not Supported...")

    print("******************************")
