exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import cnv_tk
from Toolkits import dir_tk
import os


if __name__ == '__main__':
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
            try:
                print("Reading: " + datafile)
                cast = cnv_tk.Cast(datafile)
                cnv_tk.cnv_meta(cast, datafile)
                df = cnv_tk.cnv_to_dataframe(cast)
                cnv_tk.createTripTag(cast)
                cnv_tk.cnv_write(cast, df, ext="")
            except Exception as e:
                x = input("ERROR: " + e.__str__() + "\nProgram Halted!\nPress Enter To Continue...")