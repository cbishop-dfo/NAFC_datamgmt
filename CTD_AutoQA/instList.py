import os
from Toolkits import cnv_tk
from Toolkits import dir_tk

"""
Writes all ctd instruments in a selected directory to an .inst file
"""
dir_path = os.path.dirname(os.path.realpath(__file__))
dirName = dir_path

if __name__ == '__main__':
    files = dir_tk.confirmSelection(dirName)
    InstArray = []
    for f in files:
        # changes Dir back to original after writing to trimmed sub folder
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)

            InstArray.append(cast.InstrumentName)
    outfile = cast.ship.__str__() + cast.trip.__str__() + ".inst"
    f = open(outfile, "w+")
    for l in InstArray:
        f.writelines(l + "\n")
    print(InstArray)

