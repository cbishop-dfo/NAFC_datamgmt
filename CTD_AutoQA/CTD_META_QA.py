import os
import cnv_tk
import dir_tk

def QAMeta(cast, df):

    cast.goodMETA = False
    cast.hasNullDF = True
    if cast.Latitude != "":
        if cast.Longitude != "":
            if cast.ShipName != "" or cast.ship != "":
                if cast.Instrument != "":
                    cast.goodMETA = True

    cast.hasNullDF = df.isnull().values.any()

    if not cast.hasNullDF and cast.goodMETA:
        print("QA Successful")
    else:
        print("QA Failed \nDF: " + cast.goodDF.__str__() + " META: " + cast.goodMETA.__str__())
        dir_tk.createProblemFolder()
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
            QAMeta(cast, df)
