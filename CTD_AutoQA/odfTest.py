from Toolkits import dir_tk
from Toolkits import odf_tk
from Toolkits import p_tk
import os


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
    files = dir_tk.confirmSelection(dirName)


    for f in files:
        # changes Dir back to original after writing to sub folder
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        if datafile.lower().endswith(".odf"):
            cast = odf_tk.Cast(datafile)
            odf_tk.odf_meta(cast, datafile)
            df = odf_tk.odf_to_dataframe(cast)
            p_df = p_tk.drop_non_pfile(cast, df)
            p_tk.write_pfile(cast, p_df)
            print()
