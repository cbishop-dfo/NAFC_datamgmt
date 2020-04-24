import os
import tkinter as tk
from tkinter import filedialog
import cnv_tk
import dir_tk

"""
Test script 
writes original cnv datafile with extension .old and the new modified cnv with extension ".new".

calling the cnv_write will write out the cast object created and the dataframe passed in.

Note: by changing the parameter 'ext' in the cnv_write you can change the extension of the outfile (default is '.old')
currently the new/modified file has extension '.new' rather than passing an empty string and overwriting the infile. 
This is for testing purposes.
"""

def modifyDF(new_df):
    # Column for depth/pressure typically comes after the the scan, placing it in the second column
    depth = new_df.columns.values[1]

    # Drop rows based on the condition: where depth < 2
    new_df = new_df.drop(new_df[(new_df[depth].astype(float) < 2)].index)
    return new_df

if __name__ == '__main__':

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    print("Files to Process\n[1] All Files In Current Directory\n[2] Manual File Select")
    select = input()

    if select.__eq__("2"):
        root = tk.Tk()
        root.withdraw()
        files = filedialog.askopenfilenames(title='Choose files')
        print(files)

    if select.__eq__("1"):
        files = dir_tk.getListOfFiles(dirName)

    for f in files:

        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"): # or datafile.lower().endswith(".xbt"):
            try:

                print("Reading: " + datafile)
                # Create the cast object
                cast = cnv_tk.Cast(datafile)
                # read the variables for the datafile into the cast object
                cnv_tk.cnv_meta(cast, datafile)
                # Create dataframe from the cast
                df = cnv_tk.cnv_to_dataframe(cast)
                # Write out the cast meta data with the dataframe
                cnv_tk.cnv_write(cast, df, ext=".old")
                cnv_tk.cnv_write_simple(cast, df)

                # edit/modify dataframe
                new_df = df
                new_df = modifyDF(new_df)

                # TODO: Change ".new" to an empty string "" to overwrite original, using ".new" for debugging purposes.
                # Write the cast meta data with the new/modified dataframe.
                cnv_tk.cnv_write(cast, new_df, ext=".new")

            # Except block. Stores any problem file errors in a subfolder in the current running directory. avoids crashes when processing multiple files.
            except Exception as e:
                os.chdir(dirName)
                dir_tk.createProblemFolder()
                newfile = datafile.replace(".sbe", "_") + ".error"
                print("Error Reading File" + e.__str__())
                f = open(newfile, "w")
                f.write(e.__str__())

        else:
            print("File Not Supported...")

    print("******************************")
    input("Press Enter To Finish")