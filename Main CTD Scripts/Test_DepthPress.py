from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import seawater as sw

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

            # df_press_depth creates a dataframe with both pressure and depth
            df = cnv_tk.df_press_depth(cast)
            print()



