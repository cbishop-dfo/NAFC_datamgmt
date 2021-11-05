from Toolkits import odf_tk
from Toolkits import  cnv_tk
from Toolkits import dir_tk
import os


if __name__ == '__main__':

    files = dir_tk.confirmSelection()

    for f in files:
        try:
            datafile = f.name
        except:
            datafile = f

        print("Reading: " + datafile)
        #cast = odf_tk.Cast(datafile)
        #odf_tk.odf_meta(cast, datafile)
        #df = odf_tk.odf_to_dataframe(cast)

        cast = cnv_tk.Cast(datafile)
        cnv_tk.cnv_meta(cast, datafile)
        df = cnv_tk.cnv_to_dataframe(cast)
        s_df = cnv_tk.StandardizedDF(cast, df)
        b_df = cnv_tk.BinDF(cast, s_df)
        cnv_tk.NCWrite(cast, s_df)

        #cnv_tk.cnv_write(cast, df, ext=".odfTOcnv")
