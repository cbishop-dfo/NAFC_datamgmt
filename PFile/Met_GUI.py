import tkinter as  TK
from tkinter import *
import xlrd
import xlwt


###########################################################################################################
"""
This script is for writing Meteorological data to an xlsx file.

*NOTE: File name should be created using ship_number + trip_number + _met.xlsx
so the Universal_Writer will be able to write it out for the rsbe files.


"""

# TODO: GET WORKING WITH XLSX FILES
# TODO: Add lat/lon to GUI and xlsx header
# TODO: Add year, Day and Month to GUI and xlsx header
# TODO: Add checks for invalid data in fields

def write_met():
    # Get Entry Values
    ShipBoxValue = ShipBox.get()
    TripBoxValue = TripBox.get()
    StationBoxValue = StationBox.get()
    CloudBoxValue = CloudBox.get()
    wdirBoxValue = wdirBox.get()
    wspdBoxValue = wspdBox.get()
    wwBoxValue = wwBox.get()
    pressBoxValue = pressBox.get()
    wetBoxValue = wetBox.get()
    dryBoxValue = dryBox.get()
    wavperBoxValue = wavperBox.get()
    wavheightBoxValue = wavheightBox.get()
    swelldirBoxValue = swelldirBox.get()
    swellheightBoxValue = swellheightBox.get()
    swellperBoxValue = swellperBox.get()
    icebergBoxValue = icebergBox.get()
    iceconcBoxValue = iceconcBox.get()
    icestageBoxValue = icestageBox.get()

    ID = ShipBoxValue + TripBoxValue + StationBoxValue
    filename = ShipBoxValue + TripBoxValue + "_met.xls"

    row = [ID, CloudBoxValue, wdirBoxValue, wspdBoxValue, wwBoxValue, pressBoxValue, wetBoxValue, dryBoxValue,
           wavperBoxValue, wavheightBoxValue, swelldirBoxValue, swellheightBoxValue, swellperBoxValue,
           icebergBoxValue, iceconcBoxValue, icestageBoxValue]

    try:
        # Try and read
        wb = xlrd.open_workbook(filename)
        sheet = wb.sheet_by_index(0)
        sheet.write(row)

    except:
        # If can't read, create new file
        wb = xlwt.Workbook()
        sheet = wb.add_sheet("Meteorological")
        header = ["Cloud", "WinDir", "WinSPD", "wwCode", "BarPres", "TempWet", "TempDry", "WavPeroid", "WavHeight",
                  "SwellDir", "SwellPeroid", "SwellHeight", "IceConc", "IceStage", "IceBerg"]

        for c, h in enumerate(header):
            sheet.write(0, c, h)
        wb.save(filename)
        wb = xlrd.open_workbook(filename)
        sheet = wb.sheet_by_index(0)
        sheet.write(row)


if __name__ == '__main__':
    # Create windows and frames
    root = Tk()
    root.title('Model Definition')
    root.geometry('{}x{}'.format(460, 350))
    database = "CTD.db"
    #root.state('zoomed')
    main_frame = Frame(root, relief=SUNKEN, borderwidth=10, width=5, height=5)
    main_frame.pack(side=TOP)



    # create the widgets for the top frame
    ship_label = Label(main_frame, text="Ship", fg="red", font="Times")
    ShipBox = Entry(main_frame)
    trip_label = Label(main_frame, text="Trip", fg="red", font="Times")
    TripBox = Entry(main_frame)
    station_label = Label(main_frame, text="Station", fg="red", font="Times")
    StationBox = Entry(main_frame)
    cloud_lab = Label(main_frame, text="Cloud", fg="red", font="Times")
    CloudBox = Entry(main_frame)
    wdir = Label(main_frame, text="Wind Directiom", fg="red", font="Times")
    wdirBox = Entry(main_frame)
    wspd_lab = Label(main_frame, text="Wind Speed", fg="red", font="Times")
    wspdBox = Entry(main_frame)
    ww_lab = Label(main_frame, text="WW Code", fg="red", font="Times")
    wwBox = Entry(main_frame)
    press = Label(main_frame, text="Bar Pressure", fg="red", font="Times")
    pressBox = Entry(main_frame)
    wetlab = Label(main_frame, text="Wet Temp", fg="red", font="Times")
    wetBox = Entry(main_frame)
    drylab = Label(main_frame, text="Dry Temp", fg="red", font="Times")
    dryBox = Entry(main_frame)
    wavperlab = Label(main_frame, text="Wave Peroid", fg="red", font="Times")
    wavperBox = Entry(main_frame)
    wavheight = Label(main_frame, text="Wave Height", fg="red", font="Times")
    wavheightBox = Entry(main_frame)
    swelldirlab = Label(main_frame, text="Swell Direction", fg="red", font="Times")
    swelldirBox = Entry(main_frame)
    swellperlab = Label(main_frame, text="Swell Peroid", fg="red", font="Times")
    swellperBox = Entry(main_frame)
    swellheightlab = Label(main_frame, text="Swell Height", fg="red", font="Times")
    swellheightBox = Entry(main_frame)
    iceconclab = Label(main_frame, text="Ice Concentration", fg="red", font="Times")
    iceconcBox = Entry(main_frame)
    icestagelab = Label(main_frame, text="Ice Stage", fg="red", font="Times")
    icestageBox = Entry(main_frame)
    iceberglab = Label(main_frame, text="Ice Bergs", fg="red", font="Times")
    icebergBox = Entry(main_frame)
    buttonSelect = Button(main_frame, height=1, width=10, text="Write", highlightcolor='red', highlightthickness=3,
                          command=lambda: write_met())

    # layout the widgets in the top frame
    ship_label.grid(row=0, column=0)
    ShipBox.grid(row=1, column=0)
    trip_label.grid(row=0, column=1)
    TripBox.grid(row=1, column=1)
    station_label.grid(row=0, column=2)
    StationBox.grid(row=1, column=2)

    cloud_lab.grid(row=2, column=0)
    CloudBox.grid(row=3, column=0)
    wdir .grid(row=2, column=1)
    wdirBox.grid(row=3, column=1)
    wspd_lab.grid(row=2, column=2)
    wspdBox.grid(row=3, column=2)

    ww_lab.grid(row=4, column=0)
    wwBox.grid(row=5, column=0)
    press.grid(row=4, column=1)
    pressBox.grid(row=5, column=1)

    wetlab.grid(row=6, column=0)
    wetBox.grid(row=7, column=0)
    drylab.grid(row=6, column=1)
    dryBox.grid(row=7, column=1)

    wavperlab.grid(row=8, column=0)
    wavperBox.grid(row=9, column=0)
    wavheight.grid(row=8, column=1)
    wavheightBox.grid(row=9, column=1)

    swelldirlab.grid(row=10, column=0)
    swelldirBox.grid(row=11, column=0)
    swellperlab.grid(row=10, column=1)
    swellperBox.grid(row=11, column=1)
    swellheightBox.grid(row=10, column=2)
    swellheightBox.grid(row=11, column=2)

    iceconclab.grid(row=12, column=0)
    iceconcBox.grid(row=13, column=0)
    icestagelab.grid(row=12, column=1)
    icestageBox.grid(row=13, column=1)
    iceberglab.grid(row=12, column=2)
    icebergBox.grid(row=13, column=2)

    buttonSelect.grid(row=14, column=1)

    root.mainloop()