import os
"""
Creates Yearly Log File
"""
dir_path = os.path.dirname(os.path.realpath(__file__))
dirName = dir_path



def yearly_write():
    createFolder()
    f = "cruises." + year.__str__()
    newfile = os.getcwd()
    newfile = newfile + "\\" + f
    try:
        writer = open(newfile, "a+")
    except:
        writer = open(newfile, "w+")
    line = start + ",   " + end + ",    " + shipNum + ",    " + shipName + ",    " + areaSampled + ",    " + numOfCTD + ",    " + numOfXBT  + ",    " + totalInst  + ",    " + comment + "\n"
    writer.write(line)


# If no folder called Station27 exists, creates new sub folder BadSampleSize to write files to.
def createFolder():
    # Temp variable for the path, taken from datafile
    tf = dirName.__str__().split("\\")
    # remove file name to keep only the files dir
    tf.pop()
    #tf.pop()
    newpath = ""
    for f in tf:
        newpath = newpath + f + "\\"
    #newpath = newpath + "Station27\\STN27_" + cast.CastDatetime.split("-")[0] + "\\"
    newpath = newpath + "LOG\\LOG" + year + "\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)

if __name__ == '__main__':
    print("Enter The Following\n")
    year = input("Year: ")
    start = input("Start Date(yyyy-mm-dd): ")
    end = input("End Date(yyyy-mm-dd): ")
    numDays = input("Number of Days Sampled: ")
    shipNum = input("Ship Number: ")
    shipName = input("Ship Name: ")
    areaSampled = input("Area Sampled: ")
    numOfCTD = input("Number of CTDs: ")
    numOfXBT = input("Number of XBTs: ")
    totalInst = input("Total Number of Instruments: ")
    comment = input("Comment: ")

    yearly_write()


