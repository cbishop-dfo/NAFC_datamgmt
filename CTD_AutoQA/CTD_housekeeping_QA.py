import os
from Toolkits import cnv_tk
from Toolkits import dir_tk

def QAMeta(cast, df):

    cast.goodMETA = False
    cast.hasNullDF = True
    if cast.Latitude != "":
        if cast.Longitude != "":
            if cast.ShipName != "" or cast.ship != "":
                if cast.Instrument != "":
                    cast.goodMETA = True

    cast.hasNullDF = df.isnull().values.any()

    # if no null in df and meta has all variables not empty strings then file is good
    if not cast.hasNullDF and cast.goodMETA:
        print("QA Successful")
    else:
        dir_tk.createProblemFolder()
        f = open("metalog.txt", 'a+')
        line = "QA Failed \nDF: " + cast.goodDF.__str__() + " META: " + cast.goodMETA.__str__()
        f.write(line)
        print("QA Failed \nDF: " + cast.goodDF.__str__() + " META: " + cast.goodMETA.__str__())
        cnv_tk.cnv_write(cast, df, ext=".error")

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.getListOfFiles(dirName)
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            QAMeta(cast, df) #this checks to make sure key META data variables are not empty
            
            
