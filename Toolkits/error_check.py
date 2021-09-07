exec(open("C:\QA_paths\set_QA_paths.py").read())
import pandas as pd
from Toolkits import dir_tk
from Toolkits import cnv_tk
import os
###########################################################################################################
# simple check to see if df has less than 15 rows of data
def checkdf(df, minRows=15):
    # Checking data frame for null values
    for c in df:
        length = df[c].__len__()
        nullCount = df[c].isnull().sum()
        if length - nullCount < 15:
            validDatapointCount = False
        if length == nullCount:
            print(c.__str__() + ": All Rows Null")
            # df.drop(c, axis=1)
    if len(df) < minRows:
        return False
    else:
        return True

###########################################################################################################
# compares id in filename to actual id in file
"""
Checks if ship trip station matches ID in filename
"""
def compareFilename(cast, datafile):
    uid = str(cast.ship) + str(cast.trip) + str(cast.station)
    fileID = datafile.split("/")[-1:]
    fileID = fileID[0].split(".")[0]

    if str(uid) == str(fileID):
        print("ID" + uid)
        print("FileID" + fileID)
        return True
    else:
        print("ID" + uid)
        print("FileID" + fileID)
        return False

###########################################################################################################
# compares id in filename to actual id in file
"""
Checks if ship trip station matches ID in filename
"""
def compareListOfFiles():

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

        if datafile.lower().endswith(".cnv"):
            print("File Path: " + datafile.__str__())
            # Creates Cast object
            cast = cnv_tk.Cast(datafile)

            # Populates cast variables from datafile
            cnv_tk.cnv_meta(cast, datafile)
            uid = str(cast.ship) + str(cast.trip) + str(cast.station)
            fileID = datafile.split("/")[-1:]
            fileID = fileID[0].split(".")[0]

            if str(uid) == str(fileID):
                print("ID: " + uid)
                print("FileID: " + fileID)
                print("ID's Match!\n")
                #return True
            else:
                print("ID: " + uid)
                print("FileID: " + fileID)
                print("ID's MISMATCHED!")
                input("Compare Filename to SHPTRPSTN...Press Enter To Continue\n")
                #return False

###########################################################################################################
"""
checks for pressure column
checks that column has more than 15 nan values
checks that df has at least 2 valid columns excluding scan

Writes failed QA scripts to log.txt in ProblemFiles Folder 

"""
def QADataframe(cast, df, datafile):
    hasPressure = False
    validColumnCount = False
    validDatapointCount = True

    number_of_columns = 0
    col = df.columns.values

    # Checking for pressure columns and counting valid columns
    for c in col:
        if not c.lower() == "scan":
            number_of_columns = number_of_columns + 1
        if c.lower() == "pres":
            hasPressure = True
        elif c.lower() == "depth":
            hasPressure = True
        elif c.lower() == "prdm":
            hasPressure = True
        elif c.lower() == "depsm":
            hasPressure = True
        elif c.lower() == "pressure":
            hasPressure = True


    if number_of_columns >= 2:
        validColumnCount = True

    # Checking data frame for null values
    for c in col:
        length = df[c].__len__()
        nullCount = df[c].isnull().sum()
        if length - nullCount < 15:
            validDatapointCount = False
        if length == nullCount:
            print(c.__str__() + ": All Rows Null")
            #df.drop(c, axis=1)

    if not validDatapointCount:
        dir_tk.createProblemFolder()
        f = open("log.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Enough Data points\n")

    if not hasPressure:
        dir_tk.createProblemFolder()
        f = open("log.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Pressure Column\n")

    if not validColumnCount:
        dir_tk.createProblemFolder()
        f = open("log.txt", "a+")
        f.write("File: " + datafile + " | Insufficient Number Of Data Columns; File Contains < 2 Valid Columns\n")

    if validColumnCount and validDatapointCount and hasPressure:
        print("QA Successful")
    else:
        print("QA Failed... Check 'log.txt' in 'ProblemFiles' folder for info")

###########################################################################################################

# Check if the ship trip station id is inline and matched
def checkPfileHeaderBlock(path):
    f = open(path, "r")
    f.readline()
    header1 = f.readline()
    header2 = f.readline()
    header3 = f.readline()

    if header1[0:8] == header2[0:8] and header1[0:8] == header3[0:8]:
        return True
    else:
        return False
