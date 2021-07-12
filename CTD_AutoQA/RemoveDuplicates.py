exec(open("C:\QA_paths\set_QA_paths.py").read())

from Toolkits import cnv_tk
from Toolkits import dir_tk
import pandas as pd
"""Compare and remove duplicates from selected files"""

if __name__ == '__main__':

    Remaining = []

    print("Select Main File")
    MainFile = dir_tk.selectSingleFile()
    MainFileDF = pd.read_csv(MainFile.name, delimiter="\n", header=None)

    print("Select File 1")
    File1 = dir_tk.selectSingleFile()
    File1DF = pd.read_csv(File1.name, delimiter="\n", header=None)

    print("Select File 2")
    File2 = dir_tk.selectSingleFile()
    File2DF = pd.read_csv(File2.name, delimiter="\n", header=None)

    print("Select File 3")
    File3 = dir_tk.selectSingleFile()
    File3DF = pd.read_csv(File3.name, delimiter="\n", header=None)

    for i in MainFile:
        if i in File1:
            continue

        elif i in File2:
            continue

        elif i in File3:
            continue

        else:
            Remaining.append("i")
            # TODO: Write out Remaining files

    print("Duplicates Removed.")
