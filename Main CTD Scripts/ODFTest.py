from Toolkits import odf_tk
from Toolkits import cnv_tk
from Toolkits import dir_tk
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
            cast = odf_tk.Cast(datafile)
            odf_tk.odf_meta_artic(cast, datafile)
            df = odf_tk.odf_to_dataframe(cast)
            cnv_tk.cnv_write(cast, df, ext=".cnv")

        except Exception as e:
            err = [e.__str__(), datafile]
            errorArray.append(err)
            continue

    print("Script Complete\n")
    print("*** List Of Errors ***")
    for er in errorArray:
        print("\nError: " + er[0] + "\nFilename: " + er[1])