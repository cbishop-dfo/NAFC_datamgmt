import os
from Toolkits import dir_tk
import csv

###########################################################################################################

def writeMetaToCNV(rows, csvName):

    # Write Header
    with open(csvName, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(columns[0])

    # Write Rows
    for row in rows:
        with open(csvName, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(row)


###########################################################################################################

def read_csv_to_rows(rows, columns):

    with open(datafile, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            if line[0] == "Filename":
                columns.append(line)
            else:
                rows.append(line)

###########################################################################################################

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    #files = dir_tk.getListOfFiles(dirName)
    files = dir_tk.selectFiles(dirName)
    rows = []
    csvName = "AZMP_master_META.csv"
    columns = []
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f.name
        if datafile.lower().endswith(".csv"):
            print("Reading: " + datafile)
            read_csv_to_rows(rows, columns)

    print("Writing To Master File...\nName: " + csvName + "\nLocation: " + dirName.__str__())
    writeMetaToCNV(rows, csvName)



