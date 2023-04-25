import os
import re
from Toolkits import cnv_tk
from Toolkits import dir_tk

"""
findStation27
-------------

Finds all station 27 files and copys them to a selected path.
"""
dir_path = os.path.dirname(os.path.realpath(__file__))
dirName = dir_path

def chechk27(cast):
    """
    :param cast: Cast Object (Already populated)
    :return:
    """
    #validStation = ["STATION27", "STATION 27", "STN27","STN-27","STN 27","S27","S-27","S 27"]
    #VALID_TO= ["TOSTATION27", "TOSTATION 27", "TOSTN27","TOSTN-27","TOSTN 27","TOS27","TOS-27","TOS 27"]
    VALID = False
    # Automated Check
    if cast.comment.upper().__contains__("TOSTATION 27"):
        print(cast.comment + ": VALID")
        return True
    elif cast.comment.upper().__contains__("TOSTN 27"):
        print(cast.comment + ": VALID")
        return True
    elif cast.comment.upper().__contains__("TOSTN27"):
        print(cast.comment + ": VALID")
        return True
    elif cast.comment.upper().__contains__("TOSTN-27"):
        print(cast.comment + ": VALID")
        return True
    elif cast.comment.upper().__contains__("TOS27"):
        print(cast.comment + ": VALID")
        return True

    #x = bool(re.match(re.compile("S27-??"), cast.comment.upper()))

    #if bool(re.match("S27-..", cast.comment.upper())):
    #    print(cast.comment + ": VALID")
    #    return True

    # Not explicitly 27
    elif cast.comment.upper().__contains__("STATION 27"):
        VALID = True
    elif cast.comment.upper().__contains__("STN 27"):
        VALID = True
    elif cast.comment.upper().__contains__("STN27"):
        VALID = True
    elif cast.comment.upper().__contains__("STN-27"):
        VALID = True
    elif cast.comment.upper().__contains__("S27"):
        VALID = True


    if VALID:
        print("Station 27 Comment Identified: " + cast.comment + "\n")
        sel = input("Valid Comment? y / n\n")
        if sel.lower() == "y":
            return True
        elif sel.lower() == "n":
            return False
        else:
            print("Invalid input")
            chechk27(cast)


def cnv_write27(cast, df):
    """
    :param cast: Cast Object (Already populated)
    :param df: Cast Dataframe
    :return:
    """
    createStation27Folder(cast)
    f = cast.datafile.split("/")
    f = f[f.__len__()-1]
    newfile = os.getcwd()
    newfile = newfile + "\\" + f
    writer = open(newfile, "w+")
    for l in cast.software:
        writer.write(l + "\n")
    for l in cast.userInput:
        writer.write(l + "\n")
    for l in cast.InstrumentInfo:
        writer.write(l + "\n")
    writer.write("*END*\n")
    writer.write(df.to_string(header=False, index=False))

# If no folder called Station27 exists, creates new sub folder BadSampleSize to write files to.
def createStation27Folder(cast):
    """
    :param cast: Cast Object (Already populated)
    :return:
    """
    # Temp variable for the path, taken from datafile
    tf = cast.datafile.split("/")
    # remove file name to keep only the files dir
    tf.pop()
    newpath = ""
    for f in tf:
        newpath = newpath + f + "\\"
    newpath = newpath + "Station27\\STN27_" + cast.CastDatetime.split("-")[0] + "\\"

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    # Changes dir
    os.chdir(newpath)

if __name__ == '__main__':
    files = dir_tk.confirmSelection(dirName)
    InstArray = []

    for f in files:
        # changes Dir back to original after writing to sub folder
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            is27 = False
            is27 = chechk27(cast)
            if is27:
                cnv_write27(cast, df)
                
                
#check stn27 coords, add 0.5nm tolerance.