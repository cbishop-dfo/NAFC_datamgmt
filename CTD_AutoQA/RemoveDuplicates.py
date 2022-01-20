exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import dir_tk
import pandas as pd
import sys

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

    for i in MainFileDF.values:
        match = False
        for j in File1DF.values:
            x = i[0]
            y = j[0]
            if x == y:
                match = True
                print("Match")

        for k in File2DF.values:
            x = i[0]
            y = k[0]
            if x == y:
                match = True
                print("Match")

        for l in File3DF.values:
            x = i[0]
            y = l[0]
            if x == y:
                match = True
                print("Match")

        if match == False:
            Remaining.append(i[0])
            print(len(Remaining))
            # TODO: Write out Remaining files

    print("Duplicates Removed.")
    with open("RemainingFiles.dat", "w") as f:
        for line in Remaining:
            f.write(line + "\n")
    f.close()
