import os
from Toolkits import cnv_tk
from Toolkits import dir_tk

"""
checks for pressure column
checks that column has more than 15 nan values
checks that df has at least 2 valid columns excluding scan

Writes failed QA scripts to log.txt in ProblemFiles Folder 

"""

def QADataframe(cast, df):
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

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.getListOfFiles(dirName)
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
