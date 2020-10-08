import os
from tkinter.filedialog import askopenfiles
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

###########################################################################################################

# If no subfolder called Problem_Files exists, creates new sub folder BadSampleSize to write files to.
def createProblemFolder():
    current_path = os.path.dirname(os.path.realpath(__file__))

    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\Problem_Files\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)


###########################################################################################################

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
def selectFiles(dirName):
    file = askopenfiles(mode='r')
    return file