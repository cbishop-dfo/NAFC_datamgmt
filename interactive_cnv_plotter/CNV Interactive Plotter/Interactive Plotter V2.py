# -*- coding: utf-8 -*-
"""
Interactive Plotter V. 2.0
Script file that launches a GUI application to allow the manipulation of CNV file data.

Created on Tue Mar  9 14:58:46 2021
@author: BROWNRN
"""
exec(open("C:\QA_paths\set_QA_paths.py").read())
import os
import math
from Toolkits import dir_tk
from Toolkits import cnv_tk
import tkinter as tk
import matplotlib.ticker as mtick
import matplotlib
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
        
        #Canvas and Frame variables for Tkinter GUI
        self.canvas = tk.Canvas(self.master, height=480, width=640)
        self.canvas.pack()
        self.frame = tk.Frame(self.master, bg="#3D545B")
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frame2 = tk.Frame(self.master, bg="#63767b")
        self.frame2.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        
        self.temp_var = None
        
        #Graph Variables
        self.fig = Figure(figsize=(10,5.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.plot_canvas = FigureCanvasTkAgg(self.fig,self.frame)
        self.toolbar = None
        self.tb_select_var = False
        self.graph_drawn = False
        self.meta_data = ""
        #Plotted variable names for labeling
        self.plotted_variable_names = []
        
        #List of plotted variables
        self.plotted_variables = []
        
        #column names for variables when saving
        self.selected_variable_save_names = []
        
        self.labeled_variables = []
        self.xlabel_var = "X:"
        
        #Cast and Dataframe
        self.df = None
        self.cast = None
        
        #Data lists for variables to properly plot
        self.variable_list = []
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
        self.plotted_variable_names = []
        self.plotted_variables = []
        
        #Buttons
        self.load_button = tk.Button(self.frame, text="Load CNV", command=self.load_cnv_file,height=10,width=30,bd=5)
        self.load_button.place(relx=0.40,rely=0.40)
        self.selected_variable = None
        self.var_clicked = False
        
        #For plotting selection box functionality
        self.RS = RectangleSelector(self.ax, self.line_select_callback,
                                       drawtype='box', useblit=True,
                                       button=[1, 3],  # disable middle button
                                       minspanx=5, minspany=5,
                                       lineprops=dict(color="black",linestyle="-",alpha=1),
                                       rectprops=dict(color="black",alpha=0.2),
                                       spancoords='pixels',
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
            var1 = tk.Checkbutton(frame2, text="Temperature", justify="right", bg="#63767b", bd=2, width=10, command=lambda : self.plot_variable("temperature"))
            var1.pack(side="left")
            
        if "Secondary Temperature" in variable_list:
            var2 = tk.Checkbutton(frame2, text="Secondary Temperature", justify="right", bg="#63767b", bd=2, command=lambda : self.plot_variable("secondary temperature"))
            var2.pack(side="left")
        
        if "Conductivity" in variable_list:
            var3 = tk.Checkbutton(frame2, text="Conductivity", bg="#63767b", command=lambda : self.plot_variable("conductivity"))
            var3.pack(side="left")
            
        if "Secondary Conductivity" in variable_list:
            var4 = tk.Checkbutton(frame2, text="Secondary Conductivity", bg="#63767b", command=lambda : self.plot_variable("secondary conductivity"))
            var4.pack(side="left")
            
        if "Oxygen Raw" in variable_list:    
            var5 = tk.Checkbutton(frame2, text="Oxygen Raw", bg="#63767b", command=lambda : self.plot_variable("oxygen raw"))
            var5.pack(side="left")
        
        if "Secondary Oxygen Raw" in variable_list:
            var6 = tk.Checkbutton(frame2, text="Secondary Oxygen Raw", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("secondary oxygen raw"))
            var6.pack(side="left")
         
        if "pH" in variable_list:
            var7 = tk.Checkbutton(frame2, text="pH", bg="#63767b", command=lambda : self.plot_variable("ph"))
            var7.pack(side="left")
            
        if "Chlorophyll" in variable_list:
            var8 = tk.Checkbutton(frame2, text="Chlorophyll", bg="#63767b", command=lambda : self.plot_variable("chlorophyll"))
            var8.pack(side="left")
            
        if "CDOM Fluorescence" in variable_list:
            var9 = tk.Checkbutton(frame2, text="CDOM Fluorescence", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("cdom fluorescence"))
            var9.pack(side="left")
            
        if "Photosynthetic Active Radiation" in variable_list:
            var10 = tk.Checkbutton(frame2, text="Photosynthetic Active Radiation", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("photosynthetic active radiation"))
            var10.pack(side="left")
            
        if "Transmissometer Attenuation" in variable_list:
            var11 = tk.Checkbutton(frame2, text="Transmissometer Attenuation", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("transmissometer attenuation"))
            var11.pack(side="left")
            
        if "Transmissometer Transmission" in variable_list:
            var12 = tk.Checkbutton(frame2, text="Transmissometer Transmission", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("transmissometer transmission"))
            var12.pack(side="left")
            
        if "Oxygen" in variable_list:
            var13 = tk.Checkbutton(frame2, text="Oxygen", bg="#63767b", command=lambda : self.plot_variable("oxygen"))
            var13.pack(side="left")
            
        if "Secondary Oxygen" in variable_list:
            var14 = tk.Checkbutton(frame2, text="Secondary Oxygen", bg="#63767b", command=lambda : self.plot_variable("secondary oxygen"))
            var14.pack(side="left")
            
        if "Salinity" in variable_list:
            var15 = tk.Checkbutton(frame2, text="Salinity", bg="#63767b", command=lambda : self.plot_variable("salinity"))
            var15.pack(side="left")
            
        if "Secondary Salinity" in variable_list:
            var16 = tk.Checkbutton(frame2, text="Secondary Salinity", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("secondary salinity"))
            var16.pack(side="left")
            
        if "Density" in variable_list:
            var17 = tk.Checkbutton(frame2, text="Density", bg="#63767b", command=lambda : self.plot_variable("density"))
            var17.pack(side="left")
            
        if "Secondary Density" in variable_list:
            var18 = tk.Checkbutton(frame2, text="Secondary Density", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("secondary density"))
            var18.pack(side="left")
        
        if "Oxygen Saturation" in variable_list:
            var19 = tk.Checkbutton(frame2, text="Oxygen Saturation", wraplength=60, bg="#63767b", command=lambda : self.plot_variable("oxygen saturation"))
            var19.pack(side="left")
        
        
        
        self.graph_button = tk.Button(frame, text="Graph", command=self.graph,height=10,width=30,bd=5)
        self.graph_button.place(relx=0.40,rely=0.40)
        
        
        save_button = tk.Button(frame, text="Save", command=self.save_file,height=5,width=20,bd=5)
        save_button.place(relx=0.87,rely=0.2)
        
        
        exit_button = tk.Button(frame, text="Quit", command=self.master.destroy)
        exit_button.place(relx=0.95,rely=0.96)
        
        self.load_button.destroy()
        
        
        
    def load_cnv_file(self):
        print("Load CNV File")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dirName = dir_path
    
        # Opens file selector UI
        #files = dir_tk.confirmSelection()
        files = dir_tk.selectFiles()
        for f in files:
            # changes Dir back to original after writing to sub folder
            os.chdir(dirName)
            try:
                datafile = f.name
            except:
                datafile = f
            if datafile.lower().endswith(".cnv"):
                print("Reading: " + datafile)
    
                # Creates Cast object
                cast = cnv_tk.Cast(datafile)
                self.cast = cast
    
                # Populates Cast Variables
                cnv_tk.cnv_meta(cast, datafile)
     
                # Creates a pandas dataframe from data in the Cast object
                df = cnv_tk.cnv_to_dataframe(cast)
                self.df = df
                print(df)
                
            #Applies every row of data per variable/column to their own variable
            variable_list = []
            missing_variable_list = []
            
            temp_names = ["t090C","Pressure","temp"]
            for i in temp_names:
                try:
                    temperature = df.loc[:,i]
                    self.temp_name = i
                except:
                    print("Exception: No temp")
                
            try:
                secondary_temperature = df.loc[:,"t190C"]
                self.secondary_temperature = secondary_temperature
            except:
                missing_variable_list.append("Secondary Temperature")
            
            pressure_names = ["prDM","prdM","pres","Pressure"]
            for i in pressure_names:
                try:
                    pressure = df.loc[:,i]
                    #variable_list.append("Pressure")
                except:
                    print("Exception: No Pressure")
            
            conductivity_names = ["c0S/m","Conductivity","cond"]
            for i in conductivity_names:
                try:
                    conductivity = df.loc[:,i]
                    self.conductivity_name = i
                    #variable_list.append("Conductivity")
                except:
                    print("Exception: No Conductivity")
                
            try:
                secondary_conductivity = df.loc[:,"c1S/m"]
                #variable_list.append("Secondary Conductivity")
            except:
                missing_variable_list.append("Secondary Conductivity")
                
            try:
                oxygen_raw = df.loc[:,"sbeox0V"]
                #variable_list.append("Oxygen Raw")
            except:
                missing_variable_list.append("Oxygen Raw")
                
            try:
                secondary_oxygen_raw = df.loc[:,"sbeox1V"]
                #variable_list.append("Secondary Oxygen Raw")
            except:
                missing_variable_list.append("Secondary Oxygen Raw")
            
            try:
                ph = df.loc[:,"pH"]
                #variable_list.append("pH")
            except:
                missing_variable_list.append("pH")
            
            try:
                chlorophyll = df.loc[:,"flECO-AFL"]
                #variable_list.append("Chlorophyll A Fluoresence")
            except:
                missing_variable_list.append("Chlorophyll")
                
            try:
                cdom_fluorescence = df.loc[:,"wetCDOM"]
                #variable_list.append("CDOM Fluorescence")
            except:
                missing_variable_list.append("CDOM A Fluorescence")
            
            try:
                photosynthetic_active_radiation = df.loc[:,"par/sat/log"]
                #variable_list.append("Photosynthetic Active Radiation")
            except:
                missing_variable_list.append("Photosynthetic Active Radiation")
            
            try:
                transmissometer_attenuation = df.loc[:,"CStarAt0"]
                #variable_list.append("Transmissometer Attenuation")
            except:
                missing_variable_list.append("Transmissometer Attenuation")
                
            try:
                transmissometer_transmission = df.loc[:,"CStarTr0"]
                #variable_list.append("Transmissometer Transmission")
            except:
                missing_variable_list.append("Transmissometer Transmission")
            
            try:
                oxygen = df.loc[:,"sbeox0ML/L"]
                #variable_list.append("Oxygen")
            except:
                missing_variable_list.append("Oxygen")
                
            try:
                secondary_oxygen = df.loc[:,"sbeox1ML/L"] 
                #variable_list.append("Secondary Oxygen")
            except:
                missing_variable_list.append("Secondary Oxygen")
                
            salinity_names = ["sal00","Salinity","sal"]
            for i in salinity_names:
                try:
                    salinity = df.loc[:,i]
                    self.salinity_name = i
                    #variable_list.append("Salinity")
                except:
                    print("Exception: No Salinity")
                
            try:
                secondary_salinity = df.loc[:,"sal11"]
                #variable_list.append("Secondary Salinity")
            except:
                missing_variable_list.append("Secondary Salinity")
              
            density_names = ["sigma-t00","Density","sigt"]
            for i in density_names:
                try:
                    density = df.loc[:,i]
                    self.density_name = i
                    #variable_list.append("Density")
                except:
                    print("Exception: No Density")
                
            try:
                secondary_density = df.loc[:,"sigma-t11"]
                #variable_list.append("Secondary Density")
            except:
                missing_variable_list.append("Secondary Density")
                
            try:
                oxygen_saturation = df.loc[:,"oxsatML/L"]
                #variable_list.append("Oxygen Saturation")
            except:
                missing_variable_list.append("Oxygen Saturation")
          
            
            #converts each variables data to float and adds them to a list for proper plotting
            try:
                for i in temperature:
                    self.float_temperature.append(float(i))
                if math.isnan(max(self.float_temperature)) == False:
                    variable_list.append("Temperature")
                    print("Temperature",max(self.float_temperature))
            except:
                pass
            
            try:
                for i in secondary_temperature:
                    self.float_secondary_temperature.append(float(i))
                if math.isnan(max(self.float_secondary_temperature)) == False:
                    variable_list.append("Secondary Temperature")
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
            except:
                pass
            
            try:
                for i in secondary_conductivity:
                    self.float_secondary_conductivity.append(float(i))
                if math.isnan(max(self.float_secondary_conductivity)) == False:
                    variable_list.append("Secondary Conductivity")
            except:
                pass
            
            try:
                for i in oxygen_raw:
                    self.float_oxygen_raw.append(float(i))
                if math.isnan(max(self.float_oxygen_raw)) == False:
                    variable_list.append("Oxygen Raw")
            except:
                pass
            
            try:
                for i in secondary_oxygen_raw:
                    self.float_secondary_oxygen_raw.append(float(i))
                if math.isnan(max(self.float_secondary_oxygen_raw)) == False:
                    variable_list.append("Secondary Oxygen Raw")
            except:
                pass
            
            try:
                for i in ph:
                    self.float_ph.append(float(i))
                if math.isnan(max(self.float_ph)) == False:
                    variable_list.append("pH")
            except:
                pass
            
            try:
                for i in chlorophyll:
                    self.float_chlorophyll.append(float(i))
                if math.isnan(max(self.float_chlorophyll)) == False:
                    variable_list.append("Chlorophyll")
            except:
                pass
            
            try:
                for i in cdom_fluorescence:
                    self.float_cdom_fluorescence.append(float(i))
                if math.isnan(max(self.float_cdom_fluorescence)) == False:
                    variable_list.append("CDOM Fluorescence")
            except:
                pass
            
            try:
                for i in photosynthetic_active_radiation:
                    self.float_photosynthetic_active_radiation.append(float(i))
                if math.isnan(max(self.float_photosynthetic_active_radiation)) == False:
                    variable_list.append("Photosynthetic Active Radiation")
            except:
                pass
            
            try:
                for i in transmissometer_attenuation:
                    self.float_transmissometer_attenuation.append(float(i))
                if math.isnan(max(self.float_transmissometer_attenuation)) == False:
                    variable_list.append("Transmissometer Attenuation")
            except:
                pass
            
            try:
                for i in transmissometer_transmission:
                    self.float_transmissometer_transmission.append(float(i))
                if math.isnan(max(self.float_transmissometer_transmission)) == False:
                    variable_list.append("Transmissometer Transmission")
            except:
                pass
            
            try:
                for i in oxygen:
                    self.float_oxygen.append(float(i))
                if math.isnan(max(self.float_oxygen)) == False:
                    variable_list.append("Oxygen")
            except:
                pass
            
            try:
                for i in secondary_oxygen:
                    self.float_secondary_oxygen.append(float(i))
                if math.isnan(max(self.float_secondary_oxygen)) == False:
                    variable_list.append("Secondary Oxygen")
            except:
                pass
            
            try:
                for i in salinity:
                    self.float_salinity.append(float(i))
                if math.isnan(max(self.float_salinity)) == False:
                    variable_list.append("Salinity")
            except:
                pass
            
            try:
                for i in secondary_salinity:
                    self.float_secondary_salinity.append(float(i))
                if math.isnan(max(self.float_secondary_salinity)) == False:
                    variable_list.append("Secondary Salinity")
            except:
                pass
            
            try:        
                for i in density:
                    self.float_density.append(float(i))
                if math.isnan(max(self.float_density)) == False:
                    variable_list.append("Density")
            except:
                pass
            
            try:
                for i in secondary_density:
                    self.float_secondary_density.append(float(i))
                if math.isnan(max(self.float_secondary_density)) == False:
                    variable_list.append("Secondary Density")
            except:
                pass
            
            try:
                for i in oxygen_saturation:
                    self.float_oxygen_saturation.append(float(i))
                if math.isnan(max(self.float_oxygen_saturation)) == False:
                    variable_list.append("Oxygen Saturation")
            except:
                pass
            
            
            self.variable_list = variable_list
            print(variable_list)
            self.create_widgets()
            self.meta_data = "Latitude: "+str(cast.Latitude) + "\nLongitude: "+str(cast.Longitude) + "\nShip: "+str(cast.ship) + "\nCast Date: "+cast.CastDatetime
            self.load_meta_data()
            
    def plot_variable(self,variable_name):
        """
        Plots a variable based on name passed in.
    
        Returns
        -------
        None.
    
        """
        print("Plot Variable Function")
        ax = self.ax
        not_done_var = True
        
        if variable_name == "temperature":
            ax.scatter(self.float_temperature,self.float_pressure,label="Temperature")
            self.plotted_variable_names.append("Temperature")
            self.selected_variable_save_names.append(self.temp_name)
            self.plotted_variables.append(self.float_temperature)
              
        elif variable_name == "secondary temperature":
            ax.scatter(self.float_secondary_temperature,self.float_pressure,label="Secondary Temperature")
            self.plotted_variable_names.append("Secondary Temperature")
            self.plotted_variables.append(self.float_secondary_temperature)
            self.selected_variable_save_names.append("t190C")

        elif variable_name == "conductivity":
            ax.scatter(self.float_conductivity,self.float_pressure,label="Conductivity")
            self.plotted_variable_names.append("Conductivity")
            self.plotted_variables.append(self.float_conductivity)
            self.selected_variable_save_names.append(self.conductivity_name)
                
        elif variable_name == "oxygen raw":
            ax.scatter(self.float_oxygen_raw,self.float_pressure,label="Oxygen Raw")
            self.plotted_variable_names.append("Oxygen Raw")
            self.plotted_variables.append(self.float_oxygen_raw)
            self.selected_variable_save_names.append("sbeox0V")
            
                
        elif variable_name == "secondary oxygen raw":
            ax.scatter(self.float_secondary_oxygen_raw,self.float_pressure,label="Secondary Oxygen Raw")
            self.plotted_variable_names.append("Secondary Oxygen Raw")
            self.plotted_variables.append(self.float_secondary_oxygen)
            self.selected_variable_save_names.append("sbeox1V")
 
                
        elif variable_name == "ph":
            ax.scatter(self.float_ph,self.float_pressure,label="pH")
            self.plotted_variable_names.append("pH")
            self.plotted_variables.append(self.float_pressure)
            self.selected_variable_save_names.append("pH")
            
           
                
        elif variable_name == "chlorophyll":
            ax.scatter(self.float_chlorophyll,self.float_pressure,label="Chlorophyll A Fluorescence")
            self.plotted_variable_names.append("Chlorophyll")
            self.plotted_variables.append(self.float_chlorophyll)
            self.selected_variable_save_names.append("flECO-AFL")
                
                
        elif variable_name == "cdom fluorescence":
            ax.scatter(self.float_cdom_fluorescence,self.float_pressure,label="CDOM Fluorescence")
            self.plotted_variable_names.append("CDOM Fluorescence")
            self.plotted_variables.append(self.float_cdom_fluorescence)
            self.selected_variable_save_names.append("wetCDOM")   
          
                
                
        elif variable_name == "photosynthetic active radiation":
            ax.scatter(self.float_photosynthetic_active_radiation,self.float_pressure,label="Photosynthetic Active Radiation")
            self.plotted_variable_names.append("Photosynthetic Active Radiation")
            self.plotted_variables.append(self.float_photosynthetic_active_radiation)
            self.selected_variable_save_names.append("par/sat/log")
       
                
                
        elif variable_name == "transmissometer attenuation":
            ax.scatter(self.float_transmissometer_attenuation,self.float_pressure,label="Transmissometer Attenuation")
            self.plotted_variable_names.append("Transmissometer Attenuation")
            self.plotted_variables.append(self.float_transmissometer_attenuation)
            self.selected_variable_save_names.append("CStarAt0")
                
                
        elif variable_name == "transmissometer transmission":
            ax.scatter(self.float_transmissometer_transmission,self.float_pressure,label="Transmissometer Transmission")
            self.plotted_variable_names.append("Transmissometer Transmission")
            self.plotted_variables.append(self.float_transmissometer_transmission)
            self.selected_variable_save_names.append("CStarTr0")
                
                
        elif variable_name == "oxygen":
            ax.scatter(self.float_oxygen,self.float_pressure,label="Oxygen")
            self.plotted_variable_names.append("Oxygen")
            self.plotted_variables.append(self.float_oxygen)
            self.selected_variable_save_names.append("sbeox0ML/L")
                
          
                
        elif variable_name == "secondary oxygen":
            ax.scatter(self.float_secondary_oxygen,self.float_pressure,label="Secondary Oxygen")
            self.plotted_variable_names.append("Secondary Oxygen")
            self.plotted_variables.append(self.float_secondary_oxygen)
            self.selected_variable_save_names.append("sbeox1ML/L")
         
                
        elif variable_name == "salinity":
            ax.scatter(self.float_salinity,self.float_pressure,label="Salinity")
            self.plotted_variable_names.append("Salinity")
            self.plotted_variables.append(self.float_salinity)
            self.selected_variable_save_names.append(self.salinity_name)
          
                
                
        elif variable_name == "secondary salinity":
            ax.scatter(self.float_secondary_salinity,self.float_pressure,label="Secondary Salinity")
            self.plotted_variable_names.append("Secondary Salinity")
            self.plotted_variables.append(self.float_secondary_salinity)
            self.selected_variable_save_names.append("sal11")
           
        elif variable_name == "density":
            ax.scatter(self.float_density,self.float_pressure,label="Density")
            self.plotted_variable_names.append("Density")
            self.plotted_variables.append(self.float_density)
            self.selected_variable_save_names.append(self.density_name)
            self.selected_variable_save_names.append("sigma-t00")
         
        elif variable_name == "secondary density":
            ax.scatter(self.float_secondary_density,self.float_pressure,label="Secondary Density")
            self.plotted_variable_names.append("Secondary Density")
            self.plotted_variables.append(self.float_secondary_density)
            self.selected_variable_save_names.append("sigma-t11")
        
                
                
        elif variable_name == "oxygen saturation":
            ax.scatter(self.float_oxygen_saturation,self.float_pressure,label="Oxygen Saturation")
            self.plotted_variable_names.append("Oxygen Saturation")
            self.plotted_variables.append(self.float_oxygen_saturation)
            self.selected_variable_save_names.append("oxsatML/L")
                
            
        else:
            not_done_var = False
            print("Variable not available!")
            
        if not_done_var:
            print("Done!")
        self.selected_variable = self.plotted_variables[0]
        
    def load_meta_data(self):
        """
        Creates a meta-data label

        Returns
        -------
        None.

        """
        frame = self.frame
        meta_data_label = tk.Label(frame,text=self.meta_data, bg="#63767b")
        meta_data_label.pack(side="right")
        
        
    
        
    def graph(self):
        """
        Draws and embeds graph and toolbar also has mouse listener for click events on graph

        Returns
        -------
        None.

        """
        fig = self.fig
        ax = self.ax
        self.graph_button.destroy()
        #Label for selected variable.
        active_variable_label = tk.Label(self.frame,text="Selected Variable: "+self.plotted_variable_names[0],width=20,height=5,bd=10,wraplength=100,bg="#63767b")
        active_variable_label.place(relx=0.87,rely=0.56)
        
        #Redraws plotted variables
        if self.graph_drawn:
            self.ax.clear()
            for i in self.plotted_variables:
                self.ax.scatter(i,self.float_pressure,label=self.plotted_variable_names[self.plotted_variables.index(i)])
                
                
        ##### Bottom X axis settings ###########################################################
        self.ax.grid(color="grey",linestyle="-",linewidth=0.25,alpha=1)
        self.ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f"))
        self.ax.xaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f"))
        #ax.set_yticks(range(int(min(self.float_pressure)),int(max(self.float_pressure))+30,int((int(max(float_pressure))/1.6)/10)))
        self.ax.set_yticks(range(int(min(self.float_pressure)),int(max(self.float_pressure))+30,20))
        self.ax.set_ylim(self.ax.get_ylim()[::-1])
        self.ax.set_title
        ax.set_ylabel("Y: Pressure (Depth)")
        
        #For loop for handling labeling of X axis
        for i in self.plotted_variable_names:
            if i in self.labeled_variables:
                pass
            else:
                self.xlabel_var += "/"+i
                self.labeled_variables.append(i)
                
        ax.set_xlabel(self.xlabel_var)
        print("XLabel: ",self.xlabel_var)
        ax.legend()
        
        
        if self.graph_drawn:
            self.plot_canvas.draw()
        
        if self.graph_drawn == False:
            canvas = self.plot_canvas
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, self.frame)
            toolbar.config(background="#63767b")
            toolbar.place(relx=0.2,rely=0.94)
            toolbar.update()
            canvas.get_tk_widget().pack(side="bottom",expand=True)
            self.toolbar = toolbar
            
            #Listening event for mouse clicks on plot
            fig.canvas.mpl_connect('key_press_event', self.toggle_selector)
            self.graph_drawn = True

        

        
        
    
        
                
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
        y1_index = 0
        y2_index = 0
        x1_index = 0
        x2_index = 0

        
        #These four For loops grab the index of x1,x2,y1,y2 coordinates
        for i in self.float_pressure:
            if math.isnan(i) == False:
                if round(i) == round(y1_trunc):
                    y1_index = self.float_pressure.index(i)
                    #print("y1i: "+str(i)+" y1: "+str(round(y1))+" y1_index: "+str(y1_index))
                    break
                
        for j in self.float_pressure:
            if math.isnan(j) == False:
                if round(j) == round(y2_trunc):
                    y2_index = self.float_pressure.index(j)
                    #print("y2j: "+str(j)+" y2: "+str(round(y2))+" y2_index: "+str(y2_index))
                    break
                
        for j in self.selected_variable:
            if math.isnan(j) == False:
                if round(j) == round(x1_trunc):
                    x1_index = self.selected_variable.index(j)
                    #print("x1j: "+str(j)+" y2: "+str(round(x1))+" x1_index: "+str(x1_index))
                    break
                
        for j in self.selected_variable:
            if math.isnan(j) == False:
                if round(j) == round(x2_trunc):
                    x2_index = self.selected_variable.index(j)
                    #print("x2j: "+str(j)+" y2: "+str(round(x2))+" x2_index: "+str(x2_index))
                    break
                
       
        #Handles the finding and removing of values within a plotting variable          
        stop_var = y2_index - y1_index
        increment_var = 0
        break_var = False
        for i in range(stop_var):
            if break_var:
                break
            elif math.isnan(self.selected_variable[y1_index+i]) == False:
                break_var = True
                while y1_index+increment_var <= y2_index and x1_index+increment_var >= x2_index:
                    #print(str(increment_var)+"while loop print: ",self.selected_variable[y1_index+increment_var])
                    self.selected_variable[y1_index+increment_var] = float("nan")
                    increment_var += 1
                    
                
        #Runs the graph function to erase and redraw the plot, updating it
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

    def save_file(self):
        """
        Rewrites the variable that is currently being edited and saves the CNV as a new file.

        Returns
        -------
        None.

        """
        df = self.df
        total_rows = df.shape[0]
        variable_name = self.selected_variable_save_names[0]
        
        for i in range(total_rows):
            df.loc[i,[variable_name]] = self.selected_variable[i]
                
                
        cnv_tk.cnv_write(self.cast,df,".new")
        
if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("Interactive Plotter V2.0")
    photo = tk.PhotoImage(file="icon.PNG")
    root.iconphoto(False,photo)
    app = Application(master=root)
    app.mainloop()