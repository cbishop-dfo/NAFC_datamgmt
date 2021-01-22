exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import p_tk
from Toolkits import dir_tk
import os

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.confirmSelection(dirName)

    for f in files:

        os.chdir(dirName)
        datafile = f.name

        #TODO: improve file parsing later
        if datafile.lower().__contains__(".p") and not datafile.lower().__contains__(".py"):
            try:
                # Creates the cast object
                cast = p_tk.Cast(datafile)

                # Adds QA text to be written to the new CNV, just append any wanted text to cast.QA
                cast.QA = []
                cast.QA.append("** QA Applied: converted from pfile to sCTD.")

                # Records the header info
                p_tk.read_pFile(cast, datafile)

                # Records Channel stats from the header
                p_tk.getChannelInfo(cast, datafile)

                # Creates Pandas Dataframe from the pfile
                df = p_tk.pfile_to_dataframe(cast, datafile)

                # Data limit is used alongside database if database is used (you can ignore this in this test example)
                cast.DataLimit = len(df.index)

                # Assigns meta data to the cast object ie: latitude, longitude, Sounder Depth, Meteorological data, ect
                p_tk.pfile_meta(cast, datafile)

                # Writes the pfile as a cnv
                p_tk.writeCNV(cast, df, datafile)

            except Exception as e:
                print("Error Reading File\n" + e.__str__())
                dir_tk.createProblemFolder()
                newfile = datafile.replace(".p", "_") + ".error.p"
                print("Error Reading File")
                f = open(newfile, "w")
                f.write(e.__str__())
        else:
            print("File Not Supported...")

    print("******************************")
    input("Press Enter To Finish")