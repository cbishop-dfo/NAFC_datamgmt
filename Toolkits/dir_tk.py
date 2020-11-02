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
def selectFiles():
    file = askopenfiles(mode='r')
    return file

###########################################################################################################

def confirmSelection(dirName=os.path.dirname(os.path.realpath(__file__))):
    select = input("Choose method for file selection\n[1] Read Files From: " + dirName + "\n[2] Manually Select Files\n")
    if select == "1":
        files = getListOfFiles(dirName)
        return files
    if select == "2":
        files = selectFiles()
        return files
    else:
        print("Invalid Input")
        select = input("Choose method for file selection\n[1] Read Files From: " + dirName + "\n[2] Manually Select Files\n")
        confirmSelection(select)