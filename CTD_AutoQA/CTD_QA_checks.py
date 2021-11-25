import os
import tkinter as tk
from Toolkits import dir_tk
from Toolkits import cnv_tk

"""
CTD_smallfiles_QA
-----------------
Checks for pressure column
Checks that column has more than 15 nan values
Checks that df has at least 2 valid columns excluding scan
Checks if Pressure is shallow
Checks for Ship Name, Lat/Long, Date, Sounder Depth, Cast Type, Trip Tag
 

Writes failed QA scripts to QAlog.txt in root of parsed file Folder 

"""

def QADataframe(cast, df):
    """
    :param cast: Cast Object (Already populated)
    :param df: CTD Dataframe
    :return:
    """
    hasPressure = False 
    validColumnCount = False
    validDatapointCount = True
    shallowCheck = False
    pressureNames = ["prDM","prdM","pres","Pressure"]

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
            
    #Shallow check to see if maximum Pressure value is higher than 5
    for i in pressureNames:
        try:
            pressure = df.loc[:,i]
        except:
            pass
        try:
            if max(pressure) < "5":
                shallowCheck = True
                break
        except:
            #print("No Pressure In File")
            pass
        
    if not validDatapointCount:
        #dir_tk.createProblemFolder()
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Enough Data points\n")
        print("File: " + datafile + " | Does Not Contain Enough Data points\n")

    if not hasPressure:
        #dir_tk.createProblemFolder()
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Pressure Column\n")
        print("File: " + datafile + " | Does Not Contain Pressure Column\n")

    if not validColumnCount:
        #dir_tk.createProblemFolder()
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Insufficient Number Of Data Columns; File Contains < 2 Valid Columns\n")
        print("File: " + datafile + " | Insufficient Number Of Data Columns; File Contains < 2 Valid Columns\n")
        
    if cast.ShipName == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain A Ship Name\n")
        print("File: " + datafile + " | Does Not Contain A Ship Name\n")
        
    if cast.Latitude == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Latitude\n")
        print("File: " + datafile + " | Does Not Contain Latitude\n")
        
    if cast.Longitude == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Longitude\n")
        print("File: " + datafile + " | Does Not Contain Longitude\n")
        
    if cast.CastDatetime == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Datetime\n")
        print("File: " + datafile + " | Does Not Contain Datetime\n")
        
    if cast.SounderDepth == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain Sounder Depth\n")
        print("File: " + datafile + " | Does Not Contain Sounder Depth\n")
        
    if cast.castType == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain a Cast Type\n")
        print("File: " + datafile + " | Does Not Contain a Cast Type\n")
         
    if cast.triptag == "":
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Does Not Contain a Trip Tag\n")
        print("File: " + datafile + " | Does Not Contain a Trip Tag\n")
        
    if shallowCheck:
        f = open("QAlog.txt", "a+")
        f.write("File: " + datafile + " | Contains Shallow Pressure\n")
        print("File: " + datafile + " | Contains Shallow Pressure\n")
        
        
    
        
    if validColumnCount and validDatapointCount and hasPressure:
        print("QA Successful")
    else:
        print("QA Failed... Check 'log.txt' in 'ProblemFiles' folder for info")

if __name__ == '__main__':
    #Fixes unresponsive window
    root = tk.Tk()
    
    choice = input("Choose method for file selection\n[1]Read Multiple Files:\n[2]Read Single File\n")
    #Gets list of all files in chosen files directory
    if choice == "1":
        files = dir_tk.selectSingleFile()
        file_dir = os.path.dirname(files.name)
        files = dir_tk.getListOfFiles(file_dir)
        dirName = file_dir
        
    #Gets single files name and directory
    elif choice == "2":
        files = dir_tk.selectSingleFile()
        file = files.name
        file_dir = os.path.dirname(files.name)
        print(file_dir)
        dirName = file_dir
        files = [os.path.basename(file)]
        
    for f in files:
        # changes Dir back to original after writing to sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            QADataframe(cast, df)
            #Fixes unresponsive window
            root.withdraw()
