from Toolkits import cnv_tk
from Toolkits import dir_tk
import os
import csv
from tkinter.filedialog import askopenfile
import pandas as pd
import sqlite3


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    print("Select Master File")
    file1 = askopenfile().name
    print("Select Joiner File")
    file2 = askopenfile().name

    Master = pd.read_excel(file1)
    Joiner = pd.read_excel(file2)
    newdf = pd.merge(Master, Joiner, how="left", left_on=["CRUISE_ID", "LATITUDE_DEC", "LONGITUDE_DEC", "YEAR_UTC", "MONTH_UTC", "DAY_UTC"], right_on=["Cruise ID", "Latitude", "Longitude", "Year", "Month", "Day"])
    Master["CTD_CAST_NO"] = newdf["Station"]
    Master.head()
    filename = input("Enter name for file: ")
    Master.to_excel(filename, index=False)

    print()

