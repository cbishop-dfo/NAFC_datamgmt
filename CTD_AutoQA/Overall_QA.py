exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import cnv_tk
from Toolkits import dir_tk
from Toolkits import config_deck
from Toolkits import p_tk
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
            # Creates Cast object
            cast = cnv_tk.Cast(datafile)

            # Populates cast variables from datafile
            cnv_tk.cnv_meta(cast, datafile)

            # Creates dataframe from populated Cast object
            df = cnv_tk.cnv_to_dataframe(cast)

            df = cnv_tk.StandardizedDF(cast, df)

            # Drops columns based on instrument number
            c_df = config_deck.dropColumns(cast, df)

            # Drops columns not found in pfiles
            p_df = p_tk.drop_non_pfile(cast, df)

            # Writes a cnv file using cast and passed in dataframe.
            cnv_tk.cnv_write(cast, c_df, ext=".new")

            # Bins the dataframe
            binnedDF = cnv_tk.BinDF(cast, c_df)

            # Write out NC files
            cnv_tk.NCWrite(cast, df, cast.ship + cast.trip + cast.station + ".nc")
            cnv_tk.NCWrite(cast, binnedDF,  cast.ship + cast.trip + cast.station + "Binned.nc")
            cnv_tk.NCWrite(cast, c_df,  cast.ship + cast.trip + cast.station + "Dropped.nc")

