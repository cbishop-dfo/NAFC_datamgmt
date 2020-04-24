import os
import tkinter as tk
from tkinter import filedialog
import cnv_tk as ctk
import dir_tk as dir

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
        files = dir.getListOfFiles(dirName)

    for f in files:

        os.chdir(dirName)
        datafile = f
        if datafile.lower().endswith(".cnv"):
            try:
                print("Reading: " + datafile)
                cast = ctk.Cast(datafile)
                ctk.cnv_meta(cast, datafile)
                ctk.cnv_ascii(cast)

            except Exception as e:
                os.chdir(dirName)
                dir.createProblemFolder()
                newfile = datafile.replace(".sbe", "_") + ".error"
                print("Error Reading File" + e.__str__())
                f = open(newfile, "w")
                f.write(e.__str__())

        else:
            print("File Not Supported...")

    print("******************************")
    input("Press Enter To Finish")