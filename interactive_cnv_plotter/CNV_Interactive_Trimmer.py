exec(open("C:\QA_paths\set_QA_paths.py").read())
import os
from Toolkits import dir_tk
from Toolkits import cnv_tk
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

    
def print_metadeta():
    """
    Prints Meta-Deta to the console.

    Returns
    -------
    None.

    """
    print("\n------------Meta-Deta----------------------")
    print("Rows of data: ", len(df.index))
    print("Latitude: ",cast.Latitude)
    print("Longitude: ",cast.Longitude)
    print("Ship: ",cast.ship)
    print("Cast Date: ",cast.CastDatetime)
    print("-------------------------------------------\n")
    
def load_variable(variable_name):
    """
    Plots a variable based on name passed in.

    Returns
    -------
    None.

    """
    not_done_var = True
    if variable_name == "temperature":
        ax.plot(float_temperature,float_pressure,label="Temperature")
    elif variable_name == "conductivity":
        ax.plot(float_conductivity,float_pressure,label="Conductivity")
    elif variable_name == "oxygen raw":
        ax.plot(float_oxygen_raw,float_pressure,label="Oxygen Raw")
    elif variable_name == "secondary oxygen raw":
        ax.plot(float_secondary_oxygen_raw,float_pressure,label="Secondary Oxygen Raw")
    elif variable_name == "ph":
        ax.plot(float_ph,float_pressure,label="pH")
    elif variable_name == "chlorophyll":
        ax.plot(float_chlorophyll,float_pressure,label="Chlorophyll A Fluorescence")
    elif variable_name == "cdom fluorescence":
        ax.plot(float_cdom_fluorescence,float_pressure,label="CDOM Fluorescence")
    elif variable_name == "photosynthetic active radiation":
        ax.plot(float_photosynthetic_active_radiation,float_pressure,label="Photosynthetic Active Radiation")
    elif variable_name == "transmissometer attenuation":
        ax.plot(float_transmissometer_attenuation,float_pressure,label="Transmissometer Attenuation")
    elif variable_name == "transmissometer transmission":
        ax.plot(float_transmissometer_transmission,float_pressure,label="Transmissometer Transmission")
    elif variable_name == "oxygen":
        ax.plot(float_oxygen,float_pressure,label="Oxygen")
    elif variable_name == "secondary oxygen":
        ax.plot(float_secondary_oxygen,float_pressure,label="Secondary Oxygen")
    elif variable_name == "salinity":
        ax.plot(float_salinity,float_pressure,label="Salinity")
    elif variable_name == "secondary salinity":
        ax.plot(float_secondary_salinity,float_pressure,label="Secondary Salinity")
    elif variable_name == "density":
        ax.plot(float_density,float_pressure,label="Density")
    elif variable_name == "secondary density":
        ax.plot(float_secondary_density,float_pressure,label="Secondary Density")
    elif variable_name == "oxygen saturation":
        ax.plot(float_oxygen_saturation,float_pressure,label="Oxygen Saturation")
        
    else:
        not_done_var = False
        print("Variable not available!")
        
    if not_done_var:
        print("Done!")
    

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    # Opens file selector UI
    files = dir_tk.confirmSelection()
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

            # Populates Cast Variables
            cnv_tk.cnv_meta(cast, datafile)
 
            # Creates a pandas dataframe from data in the Cast object
            df = cnv_tk.cnv_to_dataframe(cast)
            

            #Applies every row of data per variable/column to their own variable
            variable_list = []
            missing_variable_list = []
                
            try:
                temperature = df.loc[:,"t090C"]
                variable_list.append("Temperature")
            except:
                missing_variable_list.append("Temperature")
            
            try:
                pressure = df.loc[:,"prdM"]
                variable_list.append("Pressure")
            except:
                missing_variable_list.append("Pressure")
                
            try:
                conductivity = df.loc[:,"c0S/m"]
                variable_list.append("Conductivity")
            except:
                missing_variable_list.append("Conductivity")
                
            try:
                secondary_conductivity = df.loc[:,"c1S/m"]
                variable_list.append("Secondary Conductivity")
            except:
                missing_variable_list.append("Secondary Conductivity")
                
            try:
                oxygen_raw = df.loc[:,"sbeox0V"]
                variable_list.append("Oxygen Raw")
            except:
                missing_variable_list.append("Oxygen Raw")
                
            try:
                secondary_oxygen_raw = df.loc[:,"sbeox1V"]
                variable_list.append("Secondary Oxygen Raw")
            except:
                missing_variable_list.append("Secondary Oxygen Raw")
            
            try:
                ph = df.loc[:,"pH"]
                variable_list.append("pH")
            except:
                missing_variable_list.append("pH")
            
            try:
                chlorophyll = df.loc[:,"flECO-AFL"]
                variable_list.append("Chlorophyll A Fluoresence")
            except:
                missing_variable_list.append("Chlorophyll")
                
            try:
                cdom_fluorescence = df.loc[:,"wetCDOM"]
                variable_list.append("CDOM Fluorescence")
            except:
                missing_variable_list.append("CDOM A Fluorescence")
            
            try:
                photosynthetic_active_radiation = df.loc[:,"par/sat/log"]
                variable_list.append("Photosynthetic Active Radiation")
            except:
                missing_variable_list.append("Photosynthetic Active Radiation")
            
            try:
                transmissometer_attenuation = df.loc[:,"CStarAt0"]
                variable_list.append("Transmissometer Attenuation")
            except:
                missing_variable_list.append("Transmissometer Attenuation")
                
            try:
                transmissometer_transmission = df.loc[:,"CStarTr0"]
                variable_list.append("Transmissometer Transmission")
            except:
                missing_variable_list.append("Transmissometer Transmission")
            
            try:
                oxygen = df.loc[:,"sbeox0ML/L"]
                variable_list.append("Oxygen")
            except:
                missing_variable_list.append("Oxygen")
                
            try:
                secondary_oxygen = df.loc[:,"sbeox1ML/L"] 
                variable_list.append("Secondary Oxygen")
            except:
                missing_variable_list.append("Secondary Oxygen")
                
            try:
                salinity = df.loc[:,"sal00"]
                variable_list.append("Salinity")
            except:
                missing_variable_list.append("Salinity")
                
            try:
                secondary_salinity = df.loc[:,"sal11"]
                variable_list.append("Secondary Salinity")
            except:
                missing_variable_list.append("Secondary Salinity")
                
            try:
                density = df.loc[:,"sigma-t00"]
                variable_list.append("Density")
            except:
                missing_variable_list.append("Density")
                
            try:
                secondary_density = df.loc[:,"sigma-t11"]
                variable_list.append("Secondary Density")
            except:
                missing_variable_list.append("Secondary Density")
                
            try:
                oxygen_saturation = df.loc[:,"oxsatML/L"]
                variable_list.append("Oxygen Saturation")
            except:
                missing_variable_list.append("Oxygen Saturation")
        
                
            
                
          
            #Data lists for variables to properly plot
            float_temperature = []
            float_pressure = []
            float_conductivity = []
            float_secondary_conductivity = []
            float_oxygen_raw = []
            float_secondary_oxygen_raw = []
            float_ph = []
            float_chlorophyll = []
            float_cdom_fluorescence = []
            float_photosynthetic_active_radiation = []
            float_transmissometer_attenuation = []
            float_transmissometer_transmission = []
            float_oxygen = []
            float_secondary_oxygen = []
            float_salinity = []
            float_secondary_salinity = []
            float_density = []
            float_secondary_density = []
            float_oxygen_saturation = []
            float_flag = []
            
            #converts each variables data to float and adds them to a list for proper plotting
            try:
                for i in temperature:
                    float_temperature.append(float(i))
            except:
                pass
                    
            try:
                for i in pressure:
                    float_pressure.append(float(i))
            except:
                pass
                    
            
            try:
                for i in conductivity:
                    float_conductivity.append(float(i))
            except:
                pass
            
            try:
                for i in secondary_conductivity:
                    float_secondary_conductivity.append(float(i))
            except:
                pass
            
            try:
                for i in oxygen_raw:
                    float_oxygen_raw.append(float(i))
            except:
                pass
            
            try:
                for i in secondary_oxygen_raw:
                    float_secondary_oxygen_raw.append(float(i))
            except:
                pass
            
            try:
                for i in ph:
                    float_ph.append(float(i))
            except:
                pass
            
            try:
                for i in chlorophyll:
                    float_chlorophyll.append(float(i))
            except:
                pass
            
            try:
                for i in cdom_fluorescence:
                    float_cdom_fluorescence.append(float(i))
            except:
                pass
            
            try:
                for i in photosynthetic_active_radiation:
                    float_photosynthetic_active_radiation.append(float(i))
            except:
                pass
            
            try:
                for i in transmissometer_attenuation:
                    float_transmissometer_attenuation.append(float(i))
            except:
                pass
            
            try:
                for i in transmissometer_transmission:
                    float_transmissometer_transmission.append(float(i))
            except:
                pass
            
            try:
                for i in oxygen:
                    float_oxygen.append(float(i))
            except:
                pass
            
            try:
                for i in secondary_oxygen:
                    float_secondary_oxygen.append(float(i))
            except:
                pass
            
            try:
                for i in salinity:
                    float_salinity.append(float(i))
            except:
                pass
            
            try:
                for i in secondary_salinity:
                    float_secondary_salinity.append(float(i))
            except:
                pass
            
            try:        
                for i in density:
                    float_density.append(float(i))
            except:
                pass
            
            try:
                for i in secondary_density:
                    float_secondary_density.append(float(i))
            except:
                pass
            
            try:
                for i in oxygen_saturation:
                    float_oxygen_saturation.append(float(i))
            except:
                pass
                
                
            #Initializes a plot
            fig,ax = plt.subplots()
            
            plt.title("Latitude: "+str(cast.Latitude)+", "+
                      "Longitude: "+str(cast.Longitude)+", "+
                      "Ship: "+str(cast.ship)+"")
            ax.grid(color="grey",linestyle="-",linewidth=0.25,alpha=1)
            ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f"))
            ax.xaxis.set_major_formatter(mtick.FormatStrFormatter("%.2f"))
            #ax.set_yticks(range(int(min(float_pressure)),int(max(float_pressure))+30,int((int(max(float_pressure))/1.6)/10)))
            ax.set_yticks(range(int(min(float_pressure)),int(max(float_pressure))+30,100))
            ax.set_xticks(range(-20,60,5))
            ax.set_ylim(ax.get_ylim()[::-1])
            ax.set_title
            
            #Tracks plotted variables for labeling
            plotted_variables = []
            xlabel_var = "X: "
            
            print("Interactive Plotter V1.0")
            #Main menu
            while True:
                print("**************************")
                print("*         Menu           *")
                print("**************************")
                print("1: Load a variable")
                print("2: List variables")
                print("3: List missing variables")
                print("4: Load plot")
                print("5: Print Meta-Deta")
                print("Q: Quit")
                input_var = input()
                if input_var == "1":
                    variable_name_input = input("Load which variable?: ")
                    load_variable(variable_name_input.lower())
                    plotted_variables.append(variable_name_input)
                elif input_var == "2":
                    print(variable_list)
                elif input_var == "3":
                    print(missing_variable_list)
                elif input_var == "4":
                    for i in plotted_variables:
                        xlabel_var += "/"+i
                    ax.set_ylabel("Y: Pressure (Depth)")
                    ax.set_xlabel(xlabel_var)
                    ax.legend()
                    fig.show()
                elif input_var == "5":
                    print_metadeta()
                elif input_var == "Q":
                    print("Quitting")
                    break
                else:
                    print("")
                    
                    
                