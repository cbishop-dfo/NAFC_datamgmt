import os
from Toolkits import cnv_tk
from Toolkits import dir_tk

"""
instList
--------

Writes all ctd instruments in a selected directory to an .inst file
"""
dir_path = os.path.dirname(os.path.realpath(__file__))
dirName = dir_path

# Variable to count number of vertical casts
VNET = 0

if __name__ == '__main__':
    files = dir_tk.confirmSelection(dirName)
    InstArray = []
    for f in files:
        # changes Dir back to original after writing to sub folder
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f
        if datafile.lower().endswith(".cnv"):
            print("Reading: " + datafile)
            cast = cnv_tk.Cast(datafile)
            cnv_tk.cnv_meta(cast, datafile)
            try:
                if cast.VNET.upper() == "Y":
                    VNET = VNET + 1
            except:
                print()
            InstArray.append(cast.InstrumentName)
    outfile = cast.ship.__str__() + cast.trip.__str__() + ".inst"

    # Array of already processed inst
    seenAlready = []
    # Array of inst to be written out
    outArray = []

    # Count each unique inst in array
    for i in InstArray:
        if i not in seenAlready:
            number = InstArray.count(i)
            seenAlready.append(i)
            outArray.append([i, number])

    f = open(outfile, "w+")

    # Variables to keep track of totals for each type
    totalXBT = 0
    totalSBE = 0

    # Calculate totals for each type
    for n in outArray:
        if n[0].upper().__contains__("XBT"):
            totalXBT = totalXBT + int(n[1])
        else:
            totalSBE = totalSBE + int(n[1])
    f.writelines("Instrument List\n")
    for l in outArray:
        outString = l[0].__str__() + ": " + l[1].__str__()
        f.writelines(outString + "\n")

    f.writelines("\nTotals\n")
    f.writelines("No. XBT:  " + totalXBT.__str__())
    f.writelines("\nNo. SBE:  " + totalSBE.__str__())
    f.writelines("\nNo. Vertical CTDs:  " + VNET.__str__())
    Totalstn = totalXBT + totalSBE
    f.writelines("\nTotal stns:  " + Totalstn.__str__())


