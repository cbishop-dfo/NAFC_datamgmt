import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
from scipy.interpolate import make_interp_spline, BSpline
import math
import cnv_tk
import dir_tk
"""

"""




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
                cast = cnv_tk.Cast(datafile)
                cnv_tk.cnv_meta(cast, datafile)
                df = cnv_tk.cnv_sig_dataframe(cast)
                plt.show()
                cnv_tk.cnv_igoss(cast, df)


                #df = cnv_to_dataframe(datafile, cast)
                #cast.DataLimit = len(df.index)
                #database(cast, df)
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