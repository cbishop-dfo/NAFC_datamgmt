import os
import glob
import sys
from tkinter.filedialog import askopenfiles
from tkinter.filedialog import askopenfile

###########################################################################################################

# If no subfolder called Problem_Files exists, creates new sub folder to write files to.
def createProblemFolder(foldername="Problem_Files", dirName=os.path.dirname(os.path.realpath(__file__))):
    # current_path = os.path.dirname(os.path.realpath(__file__))
    current_path = dirName
    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\" + foldername + "\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)

###########################################################################################################

# If no subfolder called foldername exists, creates new sub folder to write files to.
def createFolder(foldername="NewFolder", dirName=os.path.dirname(os.path.realpath(__file__))):

    #current_path = os.path.dirname(os.path.realpath(__file__))
    current_path = dirName
    # If newpath doesnt exist, create a new folder to satisfy new path.
    newpath = current_path + "\\" + foldername + "\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)


###########################################################################################################

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    os.chdir(dirName)
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

def selectSingleFile():
    file = askopenfile(mode='r')
    return file

###########################################################################################################

def confirmSelection(dirName=os.path.dirname(os.path.realpath(__file__))):
    select = input("Choose method for file selection\n[1] Read Files From: " + dirName + "\n[2] Manually Select Files\n"  + "[3] Sys Arg\n")
    if select == "1":
        files = getListOfFiles(dirName)
        return files
    if select == "2":
        files = selectFiles()
        return files
    if select == "3":
        fileList = []
        directory = sys.argv[1]
        for filename in glob.glob(directory):
            fileList.append(filename)
        return fileList
    if select == "4":
        directory = sys.argv[1]
        wildcard = sys.argv[2]
        # file_extension = sys.argv[2]
        print(directory)
        fileList = []
        for (root, dirs, files) in os.walk(directory):
            for file in files:
                # if file.endswith(".new") or file.endswith(".cnv"):
                if file.endswith(wildcard.__str__()):
                    print(os.path.join(root, file))
                    fileList.append(os.path.join(root, file))
        files = sorted(glob.glob(directory))
        print(len(fileList))
        return fileList

    else:
        print("Invalid Input")
        select = input("Choose method for file selection\n[1] Read Files From: " + dirName + "\n[2] Manually Select Files\n")
        confirmSelection(select)

