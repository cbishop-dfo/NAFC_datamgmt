# -*- coding: utf-8 -*-
"""
Interactive Plotter V. 2.3
Script file that launches a GUI application to allow the manipulation of CNV file data.

Created on Tue Mar  9 14:58:46 2021
Last edited on Fri Dec 17, 2021
@author: BROWNRN

Notes:
    Last selected variable is the variable that will be edited
    Works with TOWS and XBTS
    Only 3 variables can be selected at a time
    Application wont load variables if the names are different than whats already coded, may have to add more names.
    Data manipulation isnt perfect
"""
exec(open("C:\QA_paths\set_QA_paths.py").read())
import os
import math
from Toolkits import dir_tk
from Toolkits import cnv_tk
import tkinter as tk
from tkinter import messagebox
import matplotlib.ticker as mtick
#import mpl_toolkits.axisartist as AA
#from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib
#import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector


class Application(tk.Frame):
    """
    Application Object. Orients Widget placement and connects functions.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.load_variables(master)
        
        #Buttons
        self.load_button = tk.Button(self.frame,
                                     text="Load CNV",
                                     command=self.load_cnv_file,
                                     height=10,
                                     width=30,
                                     bd=5)
        
        self.load_button.place(relx=0.40,rely=0.40)
        self.load_next_file_counter = 0

            
    def load_variables(self,master):
        #Canvas and Frame variables for Tkinter GUI
        self.canvas = tk.Canvas(self.master, height=480, width=640)
        self.canvas.pack()
        self.frame = tk.Frame(self.master, bg="#3D545B", relief="groove", bd=5)
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame2 = tk.Frame(self.master, bg="#63767b", relief="groove", bd=5)
        self.frame2.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        
        self.temp_var = None
        
        #Graph Variables
        self.fig = Figure(figsize=(10.3,10), dpi=105)
        self.ax = self.fig.add_subplot(1,1,1)
        self.y1_created = False
        self.y2_created = False
        self.x1_created = False
        self.x2_created = False
        
        #Extra Y axis for TOW's
        self.y1 = self.ax.twinx()
        self.y2 = self.ax.twinx()
        
        #Extra X axis for regular cnv's
        self.x1 = self.ax.twiny()
        self.x2 = self.ax.twiny()
        
        #Controls the order in which tha axis are drawn. lower values are drawn first
        self.ax.set_zorder(0)
        self.x1.set_zorder(0.5)
        self.x2.set_zorder(1) 
        self.y1.set_zorder(0.5)
        self.y2.set_zorder(1)
        
        
        self.plot_canvas = FigureCanvasTkAgg(self.fig,self.frame)
        self.toolbar = None
        self.tb_select_var = False
        self.graph_drawn = False
        self.meta_data = ""
        
        
        #column names for variables when saving
        self.selected_variable_save_names = []
        self.modified_variable_dict = {}
        
        self.labeled_variables = []
        self.xlabel_var = "X:"
        
        #Cast and Dataframe
        self.df = None
        self.cast = None
        
        #Lat and Long
        self.latitude = None
        self.longitude = None
        
        #Data lists for variables to properly plot
        self.variable_list = []
        self.float_scan = []
        self.float_temperature = []
        self.float_secondary_temperature = []
        self.float_pressure = []
        self.float_conductivity = []
        self.float_secondary_conductivity = []
        self.float_oxygen_raw = []
        self.float_secondary_oxygen_raw = []
        self.float_ph = []
        self.float_chlorophyll = []
        self.float_cdom_fluorescence = []
        self.float_photosynthetic_active_radiation = []
        self.float_transmissometer_attenuation = []
        self.float_transmissometer_transmission = []
        self.float_oxygen = []
        self.float_secondary_oxygen = []
        self.float_salinity = []
        self.float_secondary_salinity = []
        self.float_density = []
        self.float_secondary_density = []
        self.float_oxygen_saturation = []
        self.float_flag = []
        self.variable_dict = {}
        self.plotted_variable_names = []
        self.plotted_variables = []
        self.plotted_variable_limit_counter = 0
        
        
        #Keeps track of the last selected variable. This variable is the variable being edited.
        self.selected_variable = None
        


        #For gathering mouse coordinate data for variable manipulation
        self.RS = RectangleSelector(self.ax, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # disable middle button
                                               lineprops=dict(color="black",linestyle="-",alpha=1),
                                               rectprops=dict(color="black",alpha=0.2),
                                               spancoords='data',
                                               interactive=False)
        self.RSx1 = RectangleSelector(self.x1, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # disable middle button
                                               lineprops=dict(color="black",linestyle="-",alpha=1),
                                               rectprops=dict(color="black",alpha=0.2),
                                               spancoords='data',
                                               interactive=False)
        self.RSx2 = RectangleSelector(self.x2, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # disable middle button
                                               lineprops=dict(color="black",linestyle="-",alpha=1),
                                               rectprops=dict(color="black",alpha=0.2),
                                               spancoords='data',
                                               interactive=False)
        self.RSy1 = RectangleSelector(self.y1, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # disable middle button
                                               lineprops=dict(color="black",linestyle="-",alpha=1),
                                               rectprops=dict(color="black",alpha=0.2),
                                               spancoords='data',
                                               interactive=False)
        self.RSy2 = RectangleSelector(self.y2, self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # disable middle button
                                               lineprops=dict(color="black",linestyle="-",alpha=1),
                                               rectprops=dict(color="black",alpha=0.2),
                                               spancoords='data',
                                               interactive=False)
        
        
    def create_widgets(self):
        """
        Creates main widgets.
        Variable buttons, save, exit buttons.

        Returns
        -------
        None.

        """
        
        frame = self.frame
        frame2 = self.frame2
        variable_list = self.variable_list
        
        if "Temperature" in variable_list:
            self.var1_state = tk.IntVar()
            self.var1 = tk.Checkbutton(frame2, variable = self.var1_state, text="Temperature", justify="right", bg="#63767b", bd=2, width=10, command=lambda : self.plot_variable("temperature",self.var1_state.get()))
            self.var1.pack(side="left")
            
        if "Secondary Temperature" in variable_list:
            self.var2_state = tk.IntVar()
            self.var2 = tk.Checkbutton(frame2, variable = self.var2_state, text="Secondary Temperature", justify="right", bg="#63767b", bd=2, command=lambda : self.plot_variable("secondary temperature",self.var2_state.get()))
            self.var2.pack(side="left")
        
        if "Conductivity" in variable_list:
            self.var3_state = tk.IntVar()
            self.var3 = tk.Checkbutton(frame2, variable = self.var3_state, text="Conductivity", bg="#63767b", command=lambda : self.plot_variable("conductivity",self.var3_state.get()))
            self.var3.pack(side="left")
            
        if "Secondary Conductivity" in variable_list:
            self.var4_state = tk.IntVar()
            self.var4 = tk.Checkbutton(frame2, variable = self.var4_state, text="Secondary Conductivity", bg="#63767b", command=lambda : self.plot_variable("secondary conductivity",self.var4_state.get()))
            self.var4.pack(side="left")
            
        if "Oxygen Raw" in variable_list:
            self.var5_state = tk.IntVar()
            self.var5 = tk.Checkbutton(frame2, variable = self.var5_state, text="Oxygen Raw", bg="#63767b", command=lambda : self.plot_variable("oxygen raw",self.var5_state.get()))
            self.var5.pack(side="left")
        
        if "Secondary Oxygen Raw" in variable_list:
            self.var6_state = tk.IntVar()
            self.var6 = tk.Checkbutton(frame2, variable = self.var6_state, text="Secondary Oxygen Raw", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("secondary oxygen raw",self.var6_state.get()))
            self.var6.pack(side="left")
         
        if "pH" in variable_list:
            self.var7_state = tk.IntVar()
            self.var7 = tk.Checkbutton(frame2, variable = self.var7_state, text="pH", bg="#63767b", command=lambda : self.plot_variable("ph",self.var7_state.get()))
            self.var7.pack(side="left")
            
        if "Chlorophyll" in variable_list:
            self.var8_state = tk.IntVar()
            self.var8 = tk.Checkbutton(frame2, variable = self.var8_state, text="Chlorophyll", bg="#63767b", command=lambda : self.plot_variable("chlorophyll",self.var8_state.get()))
            self.var8.pack(side="left")
            
        if "CDOM Fluorescence" in variable_list:
            self.var9_state = tk.IntVar()
            self.var9 = tk.Checkbutton(frame2, variable = self.var9_state, text="CDOM Fluorescence", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("cdom fluorescence",self.var9_state.get()))
            self.var9.pack(side="left")
            
        if "Photosynthetic Active Radiation" in variable_list:
            self.var10_state = tk.IntVar()
            self.var10 = tk.Checkbutton(frame2, variable = self.var10_state, text="Photosynthetic Active Radiation", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("photosynthetic active radiation",self.var10_state.get()))
            self.var10.pack(side="left")
            
        if "Transmissometer Attenuation" in variable_list:
            self.var11_state = tk.IntVar()
            self.var11 = tk.Checkbutton(frame2, variable = self.var11_state, text="Transmissometer Attenuation", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("transmissometer attenuation",self.var11_state.get()))
            self.var11.pack(side="left")
            
        if "Transmissometer Transmission" in variable_list:
            self.var12_state = tk.IntVar()
            self.var12 = tk.Checkbutton(frame2, variable = self.var12_state, text="Transmissometer Transmission", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("transmissometer transmission",self.var12_state.get()))
            self.var12.pack(side="left")
            
        if "Oxygen" in variable_list:
            self.var13_state = tk.IntVar()
            self.var13 = tk.Checkbutton(frame2, variable = self.var13_state, text="Oxygen", bg="#63767b", command=lambda : self.plot_variable("oxygen",self.var13_state.get()))
            self.var13.pack(side="left")
            
        if "Secondary Oxygen" in variable_list:
            self.var14_state = tk.IntVar()
            self.var14 = tk.Checkbutton(frame2, variable = self.var14_state, text="Secondary Oxygen", bg="#63767b", command=lambda : self.plot_variable("secondary oxygen",self.var14_state.get()))
            self.var14.pack(side="left")
            
        if "Salinity" in variable_list:
            self.var15_state = tk.IntVar()
            self.var15 = tk.Checkbutton(frame2, variable = self.var15_state, text="Salinity", bg="#63767b", command=lambda : self.plot_variable("salinity",self.var15_state.get()))
            self.var15.pack(side="left")
            
        if "Secondary Salinity" in variable_list:
            self.var16_state = tk.IntVar()
            self.var16 = tk.Checkbutton(frame2, variable = self.var16_state, text="Secondary Salinity", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("secondary salinity",self.var16_state.get()))
            self.var16.pack(side="left")
            
        if "Density" in variable_list:
            self.var17_state = tk.IntVar()
            self.var17 = tk.Checkbutton(frame2, variable = self.var17_state, text="Density", bg="#63767b", command=lambda : self.plot_variable("density",self.var17_state.get()))
            self.var17.pack(side="left")
            
        if "Secondary Density" in variable_list:
            self.var18_state = tk.IntVar()
            self.var18 = tk.Checkbutton(frame2, variable = self.var18_state, text="Secondary Density", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("secondary density",self.var18_state.get()))
            self.var18.pack(side="left")
        
        if "Oxygen Saturation" in variable_list:
            self.var19_state = tk.IntVar()
            self.var19 = tk.Checkbutton(frame2, variable = self.var19_state, text="Oxygen Saturation", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("oxygen saturation",self.var19_state.get()))
            self.var19.pack(side="left")
        
    
        
        #self.graph_button = tk.Button(frame, text="Graph", command=self.graph,height=10,width=30,bd=5)
        #self.graph_button.place(relx=0.40,rely=0.40)
        
        
        save_button = tk.Button(frame, text="Save\n(Exit)", command = self.save_file,height=5,width=20,bd=5)
        save_button.place(relx=0.875,rely=0.096)
        
        self.next_file_button = tk.Button(frame, text="Done\n(Save: Move To Next File)", height=5, width=20, bd=5, command=lambda : self.load_next_file())
        self.next_file_button.place(relx=0.875, rely=0.25)
        
        
        #exit_button = tk.Button(frame, text="Quit", command=self.master.destroy)
        #exit_button.place(relx=0.95,rely=0.96)
        
        self.load_button.destroy()
        
    
    def load_cnv_file(self,next_file = ""):
        print("Load CNV File")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dirName = dir_path
    
        # Opens file selector UI
        #files = dir_tk.confirmSelection()
        if next_file == "":
            files = dir_tk.selectFiles()
            print(files)
            print("Picked File!")
            for f in files:
                # changes Dir back to original after writing to sub folder
                os.chdir(dirName)
                print("F in loop!!: ",f.name)
                try:
                    datafile = f.name
                except:
                    datafile = f
                if datafile.lower().endswith(".cnv"):
                    print("Reading: " + datafile)
                    #Saves the folder path of the file to be used for loading other CNV's in the directory
                    self.file_dir = str(os.path.dirname(datafile))
                    print(self.file_dir)
                    self.file_dir = self.file_dir+"/"
                    self.first_file_name = os.path.split(datafile)[1]
                    
        elif next_file != "":
            datafile = next_file
            
        self.current_file_name = os.path.split(datafile)[1]
    
        # Creates Cast object
        cast = cnv_tk.Cast(datafile)
        self.cast = cast
        

        # Populates Cast Variables
        cnv_tk.cnv_meta(cast, datafile)
        self.castVar = str(self.cast.castType)
        #print("Printing castVar: "+self.castVar)
        #print("Cast Type: "+str(self.cast.castType))
 
        # Creates a pandas dataframe from data in the Cast object
        df = cnv_tk.cnv_to_dataframe(cast)
        
        #Standardizes variable/column naming scheme
        #df = cnv_tk.StandardizedDF(cast,df)
        self.df = df
        #print(df)
                
        #Applies every row of data per variable/column to their own variable
        variable_list = []
        missing_variable_list = []
        
            
            
#--------------------------------------------------------------------------------             
        scan_names = ["scan"]
        for i in scan_names:
            try:
                scan = df.loc[:,i]
                self.scan_name = i
            except:
                missing_variable_list.append("Scan")
                print("Exception: No Scan")
#-------------------------------------------------------------------------------- 
        temp_names = ["t090C","temp","Temperature","tv290C"]
        for i in temp_names:
            try:
                temperature = df.loc[:,i]
                self.temperature_name = i
            except:
                missing_variable_list.append("Temperature")
                print("Exception: No Temperature")
#--------------------------------------------------------------------------------                
        try:
            secondary_temperature = df.loc[:,"t190C"]
            self.secondary_temperature_name = "t190C"
        except:
            missing_variable_list.append("Secondary Temperature")
#--------------------------------------------------------------------------------            
        pressure_names = ["prDM","prdM","pres","Pressure"]
        for i in pressure_names:
            try:
                pressure = df.loc[:,i]
                self.pressure_name = i
                #variable_list.append("Pressure")
            except:
                missing_variable_list.append("Pressure")
                print("Exception: No Pressure")
#--------------------------------------------------------------------------------           
        conductivity_names = ["c0S/m","Conductivity","cond"]
        for i in conductivity_names:
            try:
                conductivity = df.loc[:,i]
                self.conductivity_name = i
                #variable_list.append("Conductivity")
            except:
                missing_variable_list.append("Conductivity")
                print("Exception: No Conductivity")
#--------------------------------------------------------------------------------                
        try:
            secondary_conductivity = df.loc[:,"c1S/m"]
            self.secondary_conductivity_name = "c1S/m"
            #variable_list.append("Secondary Conductivity")
        except:
            missing_variable_list.append("Secondary Conductivity")
#--------------------------------------------------------------------------------                
        try:
            oxygen_raw = df.loc[:,"sbeox0V"]
            self.oxygen_raw_name = "sbeox0V"
            #variable_list.append("Oxygen Raw")
        except:
            missing_variable_list.append("Oxygen Raw")
#--------------------------------------------------------------------------------                
        try:
            secondary_oxygen_raw = df.loc[:,"sbeox1V"]
            self.secondary_oxygen_raw_name = "sbeox1V"
            #variable_list.append("Secondary Oxygen Raw")
        except:
            missing_variable_list.append("Secondary Oxygen Raw")
#--------------------------------------------------------------------------------    
        ph_names = ["ph","pH"]  
        for i in ph_names:
            try:
                ph = df.loc[:,"pH"]
                self.ph_name = i
                #variable_list.append("pH")
            except:
                missing_variable_list.append("pH")
                print("Exception: No pH")
#--------------------------------------------------------------------------------            
        try:
            chlorophyll = df.loc[:,"flECO-AFL"]
            self.chlorophyll_name = "flECO-AFL"
            #variable_list.append("Chlorophyll A Fluoresence")
        except:
            missing_variable_list.append("Chlorophyll")
#--------------------------------------------------------------------------------              
        try:
            cdom_fluorescence = df.loc[:,"wetCDOM"]
            self.cdom_fluorescence_name = "wetCDOM"
            #variable_list.append("CDOM Fluorescence")
        except:
            missing_variable_list.append("CDOM A Fluorescence")
#--------------------------------------------------------------------------------           
        try:
            photosynthetic_active_radiation = df.loc[:,"par/sat/log"]
            self.photosynthetic_active_radiation_name = "par/sat/log"
            #variable_list.append("Photosynthetic Active Radiation")
        except:
            missing_variable_list.append("Photosynthetic Active Radiation")
#--------------------------------------------------------------------------------
        transmissometer_attenuation_names = ["CStarAt0","Tra","tranmissometer attenuation"]
        for i in transmissometer_attenuation_names:
            try:
                transmissometer_attenuation = df.loc[:,i]
                self.transmissometer_attenuation_name = i
                #variable_list.append("Transmissometer Attenuation")
            except:
                #missing_variable_list.append("Transmissometer Attenuation")
                print("Exception: No Conductivity")
#--------------------------------------------------------------------------------               
        try:
            transmissometer_transmission = df.loc[:,"CStarTr0"]
            self.transmissometer_transmission_name = "CStarTr0"
            #variable_list.append("Transmissometer Transmission")
        except:
            missing_variable_list.append("Transmissometer Transmission")
#--------------------------------------------------------------------------------           
        try:
            oxygen = df.loc[:,"sbeox0ML/L"]
            self.oxygen_name = "sbeox0ML/L"
            #variable_list.append("Oxygen")
        except:
            missing_variable_list.append("Oxygen")
#--------------------------------------------------------------------------------               
        try:
            secondary_oxygen = df.loc[:,"sbeox1ML/L"] 
            self.secondary_oxygen_name = "sbeox1ML/L"
            #variable_list.append("Secondary Oxygen")
        except:
            missing_variable_list.append("Secondary Oxygen")
#--------------------------------------------------------------------------------               
        salinity_names = ["sal00","Salinity","sal"]
        for i in salinity_names:
            try:
                salinity = df.loc[:,i]
                self.salinity_name = i
                #variable_list.append("Salinity")
            except:
                print("Exception: No Salinity")
#--------------------------------------------------------------------------------                
        try:
            secondary_salinity = df.loc[:,"sal11"]
            self.secondary_salinity_name = "sal11"
            #variable_list.append("Secondary Salinity")
        except:
            missing_variable_list.append("Secondary Salinity")
#--------------------------------------------------------------------------------              
        density_names = ["sigma-t00","Density","sigt"]
        for i in density_names:
            try:
                density = df.loc[:,i]
                self.density_name = i
                #variable_list.append("Density")
            except:
                print("Exception: No Density")
#--------------------------------------------------------------------------------                
        try:
            secondary_density = df.loc[:,"sigma-t11"]
            self.secondary_density_name = "sigma-t11"
            #variable_list.append("Secondary Density")
        except:
            missing_variable_list.append("Secondary Density")
#--------------------------------------------------------------------------------               
        try:
            oxygen_saturation = df.loc[:,"oxsatML/L"]
            self.oxygen_saturation_name = "oxsatML/L" 
            #variable_list.append("Oxygen Saturation")
        except:
            missing_variable_list.append("Oxygen Saturation")
 #--------------------------------------------------------------------------------         
        
        #converts each variables data to float and adds them to a list for proper plotting
        try:
            for i in scan:
                self.float_scan.append(float(i))
            if math.isnan(max(self.float_scan)) == False:
                variable_list.append("Scan")
                #print("Scan",max(self.float_scan))
        except:
            pass
        
        try:
            for i in temperature:
                self.float_temperature.append(float(i))
            if math.isnan(max(self.float_temperature)) == False:
                variable_list.append("Temperature")
                self.variable_dict["temperature"] = [self.float_temperature,self.temperature_name]
                print("Temperature",max(self.float_temperature))
        except:
            pass
        
        try:
            for i in secondary_temperature:
                self.float_secondary_temperature.append(float(i))
            if math.isnan(max(self.float_secondary_temperature)) == False:
                variable_list.append("Secondary Temperature")
                self.variable_dict["secondary temperature"] = [self.float_secondary_temperature,self.secondary_temperature_name]
        except:
            pass
        
        try:
            for i in pressure:
                self.float_pressure.append(float(i))
            if math.isnan(max(self.float_pressure)) == False:
                variable_list.append("Pressure")
        except:
            pass
       
        try:
            for i in conductivity:
                self.float_conductivity.append(float(i))
            if math.isnan(max(self.float_conductivity)) == False:
                variable_list.append("Conductivity")
                self.variable_dict["conductivity"] = [self.float_conductivity,self.conductivity_name]
        except:
            pass
        
        try:
            for i in secondary_conductivity:
                self.float_secondary_conductivity.append(float(i))
            if math.isnan(max(self.float_secondary_conductivity)) == False:
                variable_list.append("Secondary Conductivity")
                self.variable_dict["secondary conductivity"] = [self.float_secondary_conductivity,self.secondary_conductivity_name]
        except:
            pass
        
        try:
            for i in oxygen_raw:
                self.float_oxygen_raw.append(float(i))
            if math.isnan(max(self.float_oxygen_raw)) == False:
                variable_list.append("Oxygen Raw")
                self.variable_dict["oxygen raw"] = [self.float_oxygen_raw,self.oxygen_raw_name]
        except:
            pass
        
        try:
            for i in secondary_oxygen_raw:
                self.float_secondary_oxygen_raw.append(float(i))
            if math.isnan(max(self.float_secondary_oxygen_raw)) == False:
                variable_list.append("Secondary Oxygen Raw")
                self.variable_dict["secondary oxygen raw"] = [self.float_secondary_oxygen_raw,self.secondary_oxygen_raw_name]
        except:
            pass
        
        try:
            for i in ph:
                self.float_ph.append(float(i))
            if math.isnan(max(self.float_ph)) == False:
                variable_list.append("pH")
                self.variable_dict["ph"] = [self.float_ph,self.ph_name]
        except:
            pass
        
        try:
            for i in chlorophyll:
                self.float_chlorophyll.append(float(i))
            if math.isnan(max(self.float_chlorophyll)) == False:
                variable_list.append("Chlorophyll")
                self.variable_dict["chlorophyll"] = [self.float_chlorophyll,self.chlorophyll_name]
        except:
            pass
        
        try:
            for i in cdom_fluorescence:
                self.float_cdom_fluorescence.append(float(i))
            if math.isnan(max(self.float_cdom_fluorescence)) == False:
                variable_list.append("CDOM Fluorescence")
                self.variable_dict["cdom fluorescence"] = [self.float_cdom_fluorescence,self.cdom_fluorescence_name]
        except:
            pass
        
        try:
            for i in photosynthetic_active_radiation:
                self.float_photosynthetic_active_radiation.append(float(i))
            if math.isnan(max(self.float_photosynthetic_active_radiation)) == False:
                variable_list.append("Photosynthetic Active Radiation")
                self.variable_dict["photosynthetic active radiation"] = [self.float_photosynthetic_active_radiation,self.photosynthetic_active_radiation_name]
        except:
            pass
        
        try:
            for i in transmissometer_attenuation:
                self.float_transmissometer_attenuation.append(float(i))
            if math.isnan(max(self.float_transmissometer_attenuation)) == False:
                variable_list.append("Transmissometer Attenuation")
                self.variable_dict["transmissometer attenuation"] = [self.float_transmissometer_attenuation,self.transmissometer_attenuation_name]
        except:
            pass
        
        try:
            for i in transmissometer_transmission:
                self.float_transmissometer_transmission.append(float(i))
            if math.isnan(max(self.float_transmissometer_transmission)) == False:
                variable_list.append("Transmissometer Transmission")
                self.variable_dict["transmissometer transmission"] = [self.float_transmissometer_transmission,self.transmissometer_transmission_name]
        except:
            pass
        
        try:
            for i in oxygen:
                self.float_oxygen.append(float(i))
            if math.isnan(max(self.float_oxygen)) == False:
                variable_list.append("Oxygen")
                self.variable_dict["oxygen"] = [self.float_oxygen,self.oxygen_name]
        except:
            pass
        
        try:
            for i in secondary_oxygen:
                self.float_secondary_oxygen.append(float(i))
            if math.isnan(max(self.float_secondary_oxygen)) == False:
                variable_list.append("Secondary Oxygen")
                self.variable_dict["secondary oxygen"] = [self.float_secondary_oxygen,self.secondary_oxygen_name]
        except:
            pass
        
        try:
            for i in salinity:
                self.float_salinity.append(float(i))
            if math.isnan(max(self.float_salinity)) == False:
                variable_list.append("Salinity")
                self.variable_dict["salinity"] = [self.float_salinity,self.salinity_name]
        except:
            pass
        
        try:
            for i in secondary_salinity:
                self.float_secondary_salinity.append(float(i))
            if math.isnan(max(self.float_secondary_salinity)) == False:
                variable_list.append("Secondary Salinity")
                self.variable_dict["secondary salinity"] = [self.float_secondary_salinity,self.secondary_salinity_name]
        except:
            pass
        
        try:        
            for i in density:
                self.float_density.append(float(i))
            if math.isnan(max(self.float_density)) == False:
                variable_list.append("Density")
                self.variable_dict["density"] = [self.float_density,self.density_name]
        except:
            pass
        
        try:
            for i in secondary_density:
                self.float_secondary_density.append(float(i))
            if math.isnan(max(self.float_secondary_density)) == False:
                variable_list.append("Secondary Density")
                self.variable_dict["secondary_density"] = [self.float_secondary_density,self.secondary_density_name]
        except:
            pass
        
        try:
            for i in oxygen_saturation:
                self.float_oxygen_saturation.append(float(i))
            if math.isnan(max(self.float_oxygen_saturation)) == False:
                variable_list.append("Oxygen Saturation")
                self.variable_dict["oxygen saturation"] = [self.float_oxygen_saturation,self.oxygen_saturation_name]
        except:
            pass
        
        
        self.variable_list = variable_list
        #print("Variables in file: ",variable_list,"\n"+"Missing Variables: ",missing_variable_list)
        #print("Variable Dict: ",self.variable_dict)
        self.create_widgets()
        self.find_cnvs()
        self.meta_data = "Latitude: "+str(cast.Latitude) + "\nLongitude: "+str(cast.Longitude) + "\nShip: "+str(cast.ship) + "\nCast Date: "+cast.CastDatetime + "\n Cast Type: " + str(cast.castType) + "\nFile Name: " + self.current_file_name
        self.latitude = cast.Latitude
        self.longitude = cast.Longitude
        #print(self.latitude,self.longitude)
        self.load_meta_data()
        
        
            
            
    def find_cnvs(self):
        self.file_list = os.listdir(self.file_dir)
        
        #Attempts to weed-out non-cnv files
        for file in self.file_list:
            if os.path.splitext(file)[1] != ".cnv":
                self.file_list.remove(file)
                
        #TODO load files that come in order after the first selected file as to not loop through it again
        for file in self.file_list:
            if file == self.first_file_name:
                self.first_file_index = self.file_list.index(file)
        
                
        print(self.file_list)
        
    def plot_variable(self,variable_name,button_state):
        """
        Either adds or removes a variable to a list to be plotted, depending on button state.
        All variables in the self.plotted_variables list will be plotted in self.graph().
    
        Returns
        -------
        None.
    
        """
        print("Plot Variable Function")
        ax = self.ax
        not_done_var = True
        
        if variable_name in self.variable_dict.keys():
            if button_state == 1:
                if self.plotted_variable_limit_counter < 3:
                    self.plotted_variable_names.append(variable_name)
                    self.plotted_variables.append(self.variable_dict[variable_name][0])
                    self.selected_variable_save_names.append(self.variable_dict[variable_name][1])
                    self.plotted_variable_limit_counter += 1
                elif self.plotted_variable_limit_counter == 3:
                    messagebox.showwarning("Limit Reached","Maximum number of plotted variables reached: "+str(self.plotted_variable_limit_counter))
            elif button_state == 0:
                self.plotted_variable_names.remove(variable_name)
                self.plotted_variables.remove(self.variable_dict[variable_name][0])
                self.selected_variable_save_names.remove(self.variable_dict[variable_name][1])
                self.plotted_variable_limit_counter -= 1
                
        try:
            self.selected_variable = self.plotted_variables[-1]
        except IndexError:
            print("IndexError: No plotted variables")
            
        print("Variable Limit Counter: ",self.plotted_variable_limit_counter) 
        print("Plotted_variables length: ",len(self.plotted_variables))
            
        #Redraws the plot/graph and updates ticks/labels    
        self.graph()
        
    def load_meta_data(self):
        """
        Creates a meta-data label

        Returns
        -------
        None.

        """
        frame = self.frame
        self.meta_data_label = tk.Label(frame,text=self.meta_data, bg="#63767b", relief="ridge", bd=3)
        #meta_data_label.pack(side="right")
        self.meta_data_label.place(relx=0.87,rely=0.45)
        print("Cast Type: "+str(self.cast.castType))
        
    
    
    def graph(self):
        """
        Draws and embeds graph and toolbar. Also has mouse listener for click events on graph.
        Handels labelling and updating of graph.

        Returns
        -------
        None.

        """
        fig = self.fig
        ax = self.ax

        #Label for selected variable.
        try:
            self.active_variable_label = tk.Label(self.frame,text="Selected Variable: "+self.plotted_variable_names[-1],width=20,height=5,wraplength=100,bg="#63767b", relief="ridge", bd=3)
            self.active_variable_label.place(relx=0.877,rely=0.64)
        except IndexError as e:
            print("No plotted variable names",e)
            
        
        #Redraws plotted variables
        #if self.graph_drawn:
        self.ax.clear()
        try:
            self.y1.clear()
        except:
            pass
        try:
            self.y2.clear()
        except:
            pass
        try:
            self.x1.clear()
        except:
            pass
        try:
            self.x2.clear()
        except:
            pass
        #Set False here as to not have extra X axis in TOW's and extra Y axis in normal graphs
        self.x1.set_visible(False)
        self.x2.set_visible(False)
        self.y1.set_visible(False)
        self.y2.set_visible(False)
        
        #plots regular graphs
        if self.castVar == "":
            if len(self.plotted_variables) == 0:
                ax.clear()
            elif len(self.plotted_variables) > 0:
                self.ax.scatter(self.plotted_variables[0],self.float_pressure,label=self.plotted_variable_names[0],color="#81b29a")
                self.ax.set_xlabel(self.plotted_variable_names[0],color="#81b29a")
                self.ax.tick_params(color="#81b29a")
                self.ax.spines["bottom"].set_color("#81b29a")
                if self.plotted_variable_limit_counter > 1:
                    self.x1.set_visible(True)
                    self.x1.scatter(self.plotted_variables[1],self.float_pressure,label=self.plotted_variable_names[1],color="#e07a5f")
                    self.x1.set_xlabel(self.plotted_variable_names[1],color="#e07a5f")
                    self.x1.xaxis.set_label_coords(0.5,1.01)
                    self.x1.tick_params(color="#e07a5f")
                    self.x1.spines["top"].set_color("#e07a5f")
                    self.x1_created = True
                    #self.x1.spines["top"].set_position(("outward",5))
                else:
                    self.x1.set_visible(False)
                if self.plotted_variable_limit_counter > 2:
                    self.x2.set_visible(True)
                    self.x2.scatter(self.plotted_variables[2],self.float_pressure,label=self.plotted_variable_names[2],color="#3d405b") #color="#f2cc8f"
                    self.x2.set_xlabel(self.plotted_variable_names[2],color="#3d405b") #color="#f2cc8f"
                    self.x2.xaxis.set_label_coords(0.5,1.1)
                    self.x2.tick_params(color="#3d405b")
                    self.x2.spines["top"].set_color("#3d405b")
                    self.x2.spines["top"].set_position(("outward",20))
                else:
                    self.x2.set_visible(False)
                
        
        #Plots TOW graphs
        elif self.castVar == "T":
            #Extra Y axis for TOW's
            if len(self.plotted_variables) == 0:
                ax.clear()
            elif len(self.plotted_variables) > 0:
                self.ax.scatter(self.float_scan,self.plotted_variables[0],label=self.plotted_variable_names[0],color="#81b29a")
                self.ax.set_ylabel(self.plotted_variable_names[0],color="#81b29a")
                self.ax.tick_params(color="#81b29a")
                self.ax.spines["left"].set_color("#81b29a")
                #self.y1.spines["right"].set_position(("outward",5))
                if self.plotted_variable_limit_counter > 1:
                    self.y1.set_visible(True)
                    self.y1.scatter(self.float_scan,self.plotted_variables[1],label=self.plotted_variable_names[1],color="#e07a5f")
                    self.y1.set_ylabel(self.plotted_variable_names[1],color="#e07a5f")
                    self.y1.yaxis.set_label_coords(1.01,.5)
                    self.y1.tick_params(color="#e07a5f")
                    self.y1.spines["right"].set_color("#e07a5f")
                    self.y1.spines["right"].set_position(("outward",5))
                else:
                    self.y1.set_visible(False)
                if self.plotted_variable_limit_counter > 2:
                    self.y2.set_visible(True)
                    self.y2.scatter(self.float_scan,self.plotted_variables[2],label=self.plotted_variable_names[2],color="#3d405b") #color="#f2cc8f"
                    self.y2.set_ylabel(self.plotted_variable_names[2],color="#3d405b") #color="#f2cc8f"
                    self.y2.yaxis.set_label_coords(1.1,.5)
                    self.y2.tick_params(color="#3d405b")
                    self.y2.spines["right"].set_color("#3d405b")
                    self.y2.spines["right"].set_position(("outward",30))
                else:
                    self.y2.set_visible(False)
                    
                
        ##### Bottom X axis settings ###########################################################
        self.ax.grid(color="grey",linestyle="-",linewidth=0.25,alpha=1)
        self.ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f"))
        self.ax.xaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f"))
        #ax.set_yticks(range(int(min(self.float_pressure)),int(max(self.float_pressure))+30,int((int(max(float_pressure))/1.6)/10)))
        if self.castVar == "":
            self.ax.set_yticks(range(int(min(self.float_pressure)),int(max(self.float_pressure))+30,20))
            #self.ax.set_xticks(range(int(min(self.float_temperature)),int(max(self.float_temperature))+30,20))
            ax.set_ylabel("Y: Pressure (Depth)")
        elif self.castVar == "T":
            ax.set_xlabel("X: Scan")
        
        if self.castVar == "":
            self.ax.set_ylim(self.ax.get_ylim()[::-1])
            #self.ax.set_xlim(self.float_scan[0],max(self.float_scan))
            
        self.ax.set_title
        
        ax.legend()
        
        
        
        #Redraws graph
        if self.graph_drawn:
            self.plot_canvas.draw()
        
        #Initializes graph
        if not self.graph_drawn:
            canvas = self.plot_canvas
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, self.frame)
            toolbar.config(relief="ridge",bd=5)
            toolbar.place(relx=0.3,rely=0.91)
            toolbar.update()
            #canvas.get_tk_widget().pack(side="bottom",expand=True)
            canvas.get_tk_widget().config(background="#63767b",relief="groove",bd=5)
            canvas.get_tk_widget().place(relx=0.01,rely=0.1,height=525)
            self.toolbar = toolbar
            
            #Listening event for mouse clicks on plot
            fig.canvas.mpl_connect('key_press_event', self.toggle_selector)
            self.graph_drawn = True
            print("plotted_variable_counter = ", self.plotted_variable_limit_counter)
            
    

    
    def find_closest_value(self, myList, N, K, cut = 0):
        """
        Returns the value in a list closest to that of value(K)

        Parameters
        ----------
        myList : List
            List to find closest value in.
        N : Int
            Length of List.
        K : Int/Float
            Value.

        Returns
        -------
        res : Tuple
            Returns a tuple of the closest value and its index.

        """
        res = myList[0]
        #parses entire list
        if cut == 0:
            for i in range(1,N,1):
                if (abs(K - res) > abs(K - myList[i])):
                    res = myList[i]
                    
        #Cuts the list length in half to only parse the first half
        elif cut == 1:
            N = round(N/2)
            for i in range(1,N,1):
                if (abs(K - res) > abs(K - myList[i])):
                    res = myList[i]
                    
        #Starts halfway through the list, parses second half of list.      
        elif cut == 2:
            start = round(N/2)
            for i in range(start,N,1):
                if (abs(K - res) > abs(K - myList[i])):
                    res = myList[i]
            
        resIndex = myList.index(res)
        
                
        return res,resIndex

         
    def line_select_callback(self,eclick, erelease):
        """
        Callback for line selection.
    
        *eclick* and *erelease* are the press and release events.
        
        Also handles removing of values from plotted variables
        """
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        print(f"({x1:3.2f}, {y1:3.2f}) --> ({x2:3.2f}, {y2:3.2f})")
        print(f" The buttons you used were: {eclick.button} {erelease.button}")
        

        #Truncated coordinate variables
        x1_trunc = self.truncate(x1,4)
        x2_trunc = self.truncate(x2,4)
        y1_trunc = self.truncate(y1,4)
        y2_trunc = self.truncate(y2,4)
        
        
        #Index variables
        y1_index = int
        y2_index = int
        x1_index = int
        x2_index = int
        
        #Parses and removes data in two halves as to avoid finding a similar value too far
        #from the value closest to the first coordinate. Prevents removing large amounts of 
        #values when not intended. 
        ############## Parses first half of list###############################
        if self.castVar == "":
            x1_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),x1_trunc,1)[1]
            x2_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),x2_trunc,1)[1]
            y1_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y1_trunc,1)[1]
            y2_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y2_trunc,1)[1]
        elif self.castVar == "T":
            x1_index = self.find_closest_value(self.float_scan,len(self.float_scan),x1_trunc,1)[1]
            x2_index = self.find_closest_value(self.float_scan,len(self.float_scan),x2_trunc,1)[1]
            y1_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y1_trunc,1)[1]
            y2_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y2_trunc,1)[1]
    
        print("x1_Index: ",x1_index," x1_Index Value: ",self.selected_variable[x1_index],
              "\nx2_index: ",x2_index," x2_Index Value: ",self.selected_variable[x2_index],
              "\ny1_index: ",y1_index," y1_Index Value: ",self.selected_variable[y1_index],
              "\ny2_index: ",y2_index," y2_Index Value: ",self.selected_variable[y2_index])
        
        #Determines which index to start removing data at
        if x1_index > x2_index:
            indexRange = x1_index - x2_index
            startIndex = x2_index
        elif x2_index > x1_index:
            indexRange = x2_index - x1_index
            startIndex = x1_index
        else:
            indexRange = x1_index - x2_index
            
        if y1_index > y2_index:
            yIndexRange = y1_index - y2_index
            yStartIndex = y2_index
        elif y2_index > y1_index:
            yIndexRange = y2_index - y1_index
            yStartIndex = y1_index
        else:
            yIndexRange = y1_index - y2_index
        
        #For Debugging
        #removedList = []

        #if self.castVar == "":
        print("Number of Values Removed: ", indexRange)
        for i in range(indexRange):
            if self.selected_variable[startIndex+i] != float("NaN"):
                #removedList.append(self.selected_variable[startIndex+i])
                self.selected_variable[startIndex+i] = float("NaN")


        ######### Parses second half of list ###################################
        if self.castVar == "":
            x1_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),x1_trunc,2)[1]
            x2_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),x2_trunc,2)[1]
            y1_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y1_trunc,2)[1]
            y2_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y2_trunc,2)[1]
        elif self.castVar == "T":
            x1_index = self.find_closest_value(self.float_scan,len(self.float_scan),x1_trunc,2)[1]
            x2_index = self.find_closest_value(self.float_scan,len(self.float_scan),x2_trunc,2)[1]
            y1_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y1_trunc,2)[1]
            y2_index = self.find_closest_value(self.selected_variable,len(self.selected_variable),y2_trunc,2)[1]
    
        print("x1_Index: ",x1_index," x1_Index Value: ",self.selected_variable[x1_index],
              "\nx2_index: ",x2_index," x2_Index Value: ",self.selected_variable[x2_index],
              "\ny1_index: ",y1_index," y1_Index Value: ",self.selected_variable[y1_index],
              "\ny2_index: ",y2_index," y2_Index Value: ",self.selected_variable[y2_index])
        
        if x1_index > x2_index:
            indexRange = x1_index - x2_index
            startIndex = x2_index
        elif x2_index > x1_index:
            indexRange = x2_index - x1_index
            startIndex = x1_index
            
        if y1_index > y2_index:
            yIndexRange = y1_index - y2_index
            yStartIndex = y2_index
        elif y2_index > y1_index:
            yIndexRange = y2_index - y1_index
            yStartIndex = y1_index
        else:
            yIndexRange = y1_index - y2_index
         
            
        #For debugging
        #print("Number of Values Removed Second Time: ", indexRange)   
        
        #For loop value removal
        #if self.castVar == "":
        for i in range(indexRange):
            if self.selected_variable[startIndex+i] != float("NaN"):
                #removedList.append(self.selected_variable[startIndex+i])
                self.selected_variable[startIndex+i] = float("NaN")

            
        #Debug, lists values removed
        #print("Items Removed: ",removedList)
        
        #Adds the currently selected variable which was just modified to a dict of modified variables
        #All modified variables will be saved.
        self.modified_variable_dict[self.selected_variable_save_names[-1]] = self.selected_variable

            
        #Runs the graph function to erase and redraw the plot; updating it
        self.graph()
        
    def toggle_selector(self,event):
        """
        Enables/Disables the rectangle selection box for gathering X and Y coords

        Parameters
        ----------
        event : Key
            T toggles Selection Box.

        Returns
        -------
        None.

        """
        print(' Key pressed.')
        if event.key == 't':
            if self.RS.active:
                print(' RectangleSelector deactivated.')
                self.RS.set_active(False)
            else:
                print(' RectangleSelector activated.')
                self.RS.set_active(True)
            

    
    def truncate(self,i,j):
        """
        Parameters
        ----------
        i : Float
             Float which needs to be truncated.
        j : Float
            Decimal places to truncate to.

        Returns
        -------
        Float
            Returns a truncated float
        """
        if i > 0:
            return math.floor(i * 10 ** j) / 10 ** j
        elif i < 0:
            return math.ceil(i * 10 ** j) / 10 ** j

    def reset_variables(self):
        self.canvas.destroy()
        self.load_variables(None)
        
        
    def load_next_file(self):
        '''
        Starting with the index of the first file loaded, this function will load every file after it by index
        one after the other.

        Returns
        -------
        None.

        '''
        self.first_file_index += 1
        self.reset_variables()
        try:
            self.next_file = self.file_dir + self.file_list[self.first_file_index]
        except IndexError as e:
            print("Last file in list/directory",e)
            messagebox.showwarning("Last File","Last file in list/directory. No more can be loaded.")
            
        self.load_cnv_file(self.next_file)
        
        self.graph()
        
        print(self.next_file)
        
        
        
    def save_file(self,close = True):
        """
        Rewrites the variable that is currently being edited and saves the CNV as a new file.

        Returns
        -------
        None.

        """
        df = self.df
        total_rows = df.shape[0]
        #variable_name = self.selected_variable_save_names[0]
        
        
        for variable in self.modified_variable_dict:
            for i in range(total_rows):
                df.loc[i,[variable]] = self.modified_variable_dict[variable][i]

                                
        cnv_tk.cnv_write(self.cast,df,".new")
        
        if close:
            print("Quitting")
            self.master.destroy()
        elif not close:
            pass
            #Open next file in directory
            
        
if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Interactive Plotter V2.3")
    try:
        photo = tk.PhotoImage(file="icon.PNG")
        root.iconphoto(False,photo)
    except:
        print("Missing Icon. Icon won't be loaded.")
    app = Application(master=root)
    app.mainloop()