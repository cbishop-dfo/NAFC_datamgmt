import shutil
import time
from openpyxl import Workbook
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas as pd
import sys
from pylab import rcParams
# sys.path.append(os.getcwd())
from Toolkits import p_tk
from Toolkits import dir_tk
import plotly as plot
from matplotlib.widgets import Button
import matplotlib.gridspec as gridspec
import pathlib
import threading


def loaddata(datafile):
    # Creates the cast object
    cast = p_tk.Cast(datafile)

    # Records the header info
    p_tk.read_pFile(cast, datafile)

    # Records Channel stats from the header
    p_tk.getChannelInfo(cast, datafile)

    # Creates Pandas Dataframe from the pfile
    df = p_tk.pfile_to_dataframe(cast, datafile)

    # Assigns meta data to the cast object ie: latitude, longitude, Sounder Depth, Meteorological data, ect
    p_tk.pfile_meta(cast, datafile)

    return [cast, df]


########################################################################################
# MAIN PART OF PROGRAM
########################################################################################
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path
    pd.options.plotting.backend = "plotly"

    files = dir_tk.getListOfFiles(dirName)
    for files in sorted(glob.glob('*.p[0-9][0-9][0-9][0-9]')):
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        datafile = files
        data = loaddata(datafile)
        cast = data[0]
        df = data[1]
        fig = df.plot()
        fig.show()
        print("Plotting " + datafile.__str__())
        input("Press Enter To Load Next File")
