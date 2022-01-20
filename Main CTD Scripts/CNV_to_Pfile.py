from Toolkits import odf_tk
from Toolkits import cnv_tk
from Toolkits import dir_tk
from Toolkits import p_tk
import os

if __name__ == '__main__':

    files = dir_tk.confirmSelection()
    errorArray = []

    for f in files:
        try:
            datafile = f.name
        except:
            datafile = f

        try:
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            df = cnv_tk.cnv_to_dataframe(cast)
            p_tk.populateChannelStats(cast, df)
            p_tk.write_pfile(cast, df)


        except Exception as e:
            err = [e.__str__(), datafile]
            errorArray.append(err)
            continue

    print("Script Complete\n")
    print("*** List Of Errors ***")
    for er in errorArray:
        print("\nError: " + er[0] + "\nFilename: " + er[1])