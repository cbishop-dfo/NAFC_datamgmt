import pandas as pd
import datetime
import tkinter as tk
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import os



filename="nafc_pfile_list.xlsx" #this is the master list of all pfile headers prepared in excel
bottle_fname='AZMP_Bottle_Data_edit.xlsx'


def load_pfile_masterheaders():
    df = pd.read_excel(filename)
    df['LONGITUDE']=(df['LON_DEG'].abs()+df['LON_MIN']/60)*-1
    df['LATITUDE']=df['LAT_DEG']+df['LAT_MIN']/60
    #df[["day", "month", "year"]] = df['DATE'].str.split("-", expand = True)
    
    df["DATE"] = pd.to_datetime(df["DATE"])
    df['YEAR'], df['MONTH'], df['DAY'] = df['DATE'].dt.year, df['DATE'].dt.month, df['DATE'].dt.day
    df['SHPTRPSTN'] = df['SHPTRPSTN'].astype(str)
    df['SHIP#'] = df['SHPTRPSTN'].str[:2]
    df['TRIP'] = df['SHPTRPSTN'].str[2:5]
    df['STN'] = df['SHPTRPSTN'].str[5:8]
    #df['SHIP#'] = df['SHIP#'].astype(int)
    #df['TRIP'] = df['TRIP'].astype(int)
    

    return df


def load_masterbottle():
    bottle_df = pd.read_excel(bottle_fname)
    # df['LONGITUDE']=(df['LON_DEG'].abs()+df['LON_MIN']/60)*-1
    # df['LATITUDE']=df['LAT_DEG']+df['LAT_MIN']/60
    # #df[["day", "month", "year"]] = df['DATE'].str.split("-", expand = True)
    
    bottle_df["Date"] = pd.to_datetime(bottle_df["Date"])
    bottle_df['YEAR'], bottle_df['MONTH'], bottle_df['DAY'] = bottle_df['Date'].dt.year, bottle_df['Date'].dt.month, bottle_df['Date'].dt.day
    bottle_df['Ship_Trip_Stn'] = bottle_df['Ship_Trip_Stn'].astype(str)
    bottle_df['SHIP#'] = bottle_df['Ship_Trip_Stn'].str[:2]
    bottle_df['TRIP'] = bottle_df['Ship_Trip_Stn'].str[2:5]
    bottle_df['SHIP#'] = bottle_df['SHIP#'].astype(int)
    bottle_df['TRIP'] = bottle_df['TRIP'].astype(int)
    
    return bottle_df


def save_to_excel(filtered_df, excel_filename):
    
    # Save the filtered dataframe to the new excel file
    filtered_df.to_excel(excel_filename, index=False)
    

# def save_bottle_to_excel(filtered_bottle_df,excel_filename)
    
#     # Create the filename using the date and time of the query
#     # Save the filtered dataframe to the new excel file
#     filtered_bottle_df.to_excel(bot_file_name, index=False)
  



def plot_map(df, column_latitude, column_longitude, file_name_map, color):
    
    # Create a new figure window
    plt.figure()
    # Set up the Basemap instance
    
    m = Basemap(projection='merc',
                llcrnrlat=df[column_latitude].min() - 1.5,
                urcrnrlat=df[column_latitude].max() + 1.5,
                llcrnrlon=df[column_longitude].min() - 1.5,
                urcrnrlon=df[column_longitude].max() + 1.5,
                lat_ts=20, resolution='h')

    # Convert latitude and longitude to the projection coordinates
    x, y = m(df[column_longitude].values, df[column_latitude].values)

    # Draw the coastlines
    m.drawcoastlines()

    # Plot the dots on the map
    m.scatter(x, y, s=1, color=color, alpha=0.5)

    # Add a title to the plot
    plt.title('Filtered Results: {}'.format(file_name_map))

    # Show the plot
    plt.show()
    #plt.get_current_fig_manager().window.showMaximized()
    
    # Save the plot with the formatted date and time as part of the filename
    plt.savefig(file_name_map, dpi=300, bbox_inches='tight')


def search_data():
    # Get the search queries from the Entry widgets
    #ship_name_query = ship_name_entry.get()
    
    ship = ship_entry.get()
    trip = trip_entry.get()
    year = year_entry.get()
    month = month_entry.get()
    day = day_entry.get()
    latitude_lower = latitude_lower_entry.get()
    latitude_upper = latitude_upper_entry.get()
    longitude_lower = longitude_lower_entry.get()
    longitude_upper = longitude_upper_entry.get()
    
    # Get the current date and time
    now = datetime.datetime.now()
    
    # Load the Excel file into a pandas DataFrame
    df = load_pfile_masterheaders()
    bottle_df= load_masterbottle()
    
        
    #begin filtering:
    filtered_df = df
    
    filtered_bottle_df = bottle_df
    
    
    if ship:
        filtered_df = filtered_df[filtered_df['SHIP#'] == str(ship)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['SHIP#'] == int(ship)]
        
    if trip:
        filtered_df = filtered_df[filtered_df['TRIP'] == str(trip)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['TRIP'] == int(trip)]

    if year:
        filtered_df = filtered_df[filtered_df['YEAR'] == int(year)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['YEAR'] == int(year)]
    
    if month:
        filtered_df = filtered_df[filtered_df['MONTH'] == int(month)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['MONTH'] == int(month)]
    
    if day:
        filtered_df = filtered_df[filtered_df['DAY'] == int(day)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['DAY'] == int(day)]
    
    if latitude_lower:
        filtered_df = filtered_df[filtered_df['LATITUDE'] >= float(latitude_lower)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['Latitude'] >= float(latitude_lower)]
        
    if latitude_upper:
        filtered_df = filtered_df[filtered_df['LATITUDE'] <= float(latitude_upper)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['Latitude'] <= float(latitude_upper)]
        
    if longitude_lower:
        filtered_df = filtered_df[filtered_df['LONGITUDE'] >= float(longitude_lower)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['Longitude'] >= float(longitude_lower)]
        
    if longitude_upper:
        filtered_df = filtered_df[filtered_df['LONGITUDE'] <= float(longitude_upper)]
        filtered_bottle_df = filtered_bottle_df[filtered_bottle_df['Longitude'] <= float(longitude_upper)]
    
    
    #print(filtered_df)
    #print(filtered_bottle_df)
    
    # Get the current date and time
    now = datetime.datetime.now()
    
    
    
    #create the filenames using the time of the query
    filename_ctd_map = f"filtered_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_ctdmap.jpeg"

    filename_bottle_map = f"filtered_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_bottlemap.jpeg"

    filename_ctd_excel = f"filtered_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_ctd.xlsx"
    
    filename_bot_excel = f"filtered_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_bottle.xlsx"
    
    filename_ctd_filenames = f"filtered_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}_ctdfilenames.csv"
    
    
    
    
    if not filtered_df.empty:
        #ctd map
        plot_map(filtered_df,'LATITUDE','LONGITUDE',filename_ctd_map,color='red')
        #SAVE THE FILENAMES SO THE ctds CAN BE COPIED (USES BASH SCRIPT ON LINUX SO ASCII MUST BE UTF-8 AND UNIX LINE SEPERATORS)
        filtered_df[['FILENAME']].to_csv(filename_ctd_filenames, sep='\t', index=False, line_terminator='\n', encoding='utf-8')
        # Save the filtered dataframe to a new excel file
        save_to_excel(filtered_df,filename_ctd_excel)
    
    
    if not filtered_bottle_df.empty:
        #bottle map
        plot_map(filtered_bottle_df,'Latitude','Longitude',filename_bottle_map,color='blue')
        save_to_excel(filtered_bottle_df, filename_bot_excel)

    
    
    #if path doesn’t exist we create a new path
    
    try:
        query_folder=f"filtered_data_{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}"
        os.makedirs(query_folder)
    except FileExistsError:
        # directory already exists
        pass
   
    
    # specify the path of the subdirectory to move the file to
    subdir_path = query_folder
    
    
    if not filtered_df.empty:
        # specify the path of the file to move
        file_to_move1 = filename_ctd_map
        file_to_move3 = filename_ctd_excel
        file_to_move5 = filename_ctd_filenames
    
    
        # construct the new path for the file
        new_file_path1 = os.path.join(subdir_path, file_to_move1)
        new_file_path3 = os.path.join(subdir_path, file_to_move3)
        new_file_path5 = os.path.join(subdir_path, file_to_move5)
        
        # move the file to the new location
        os.rename(os.path.normpath(file_to_move1), os.path.normpath(new_file_path1))
        os.rename(os.path.normpath(file_to_move3), os.path.normpath(new_file_path3))
        os.rename(os.path.normpath(file_to_move5), os.path.normpath(new_file_path5))
    
    
    
    
    if not filtered_bottle_df.empty:
        file_to_move2 = filename_bottle_map
        file_to_move4 = filename_bot_excel
    
        # construct the new path for the file
        
        new_file_path2 = os.path.join(subdir_path, file_to_move2)
        new_file_path4 = os.path.join(subdir_path, file_to_move4)
    
    
        # move the file to the new location
        os.rename(os.path.normpath(file_to_move2), os.path.normpath(new_file_path2))
        os.rename(os.path.normpath(file_to_move4), os.path.normpath(new_file_path4))
    
   
    
    
    
    
    # Replace these with the actual data
    num_entries_filtered_df = len(filtered_df.index)
    num_entries_filtered_bottle_df = len(filtered_bottle_df.index)
    end_now = datetime.datetime.now()
    time_delta = end_now - now
    # Convert the timedelta to a float representing the total number of seconds
    seconds = time_delta.total_seconds()
    
    # Create a Tkinter window
    rootmsg = tk.Tk()
    
    # Create a label with the desired message
    message = f"# of Filtered CTD Results: {num_entries_filtered_df}, \n# of Filtered Bottle Results: {num_entries_filtered_bottle_df}\nTime taken to Query: {seconds:.2f} seconds"
    label = tk.Label(rootmsg, text=message)
    label.pack()
    
    # Run the Tkinter event loop
    rootmsg.mainloop()


#Create the tkinter window


root = tk.Tk()
root.title("Data Search")


ship_label = tk.Label(root, text="SHIP #:")
ship_label.pack()
ship_entry = tk.Entry(root)
ship_entry.pack()

trip_label = tk.Label(root, text="TRIP #:")
trip_label.pack()
trip_entry = tk.Entry(root)
trip_entry.pack()


year_label = tk.Label(root, text="Year:")
year_label.pack()
year_entry = tk.Entry(root)
year_entry.pack()

month_label = tk.Label(root, text="Month:")
month_label.pack()
month_entry = tk.Entry(root)
month_entry.pack()

day_label = tk.Label(root, text="Day:")
day_label.pack()
day_entry = tk.Entry(root)
day_entry.pack()

latitude_lower_label = tk.Label(root, text="Lower bound Latitude:")
latitude_lower_label.pack()
latitude_lower_entry = tk.Entry(root)
latitude_lower_entry.pack()

latitude_upper_label = tk.Label(root, text="Upper bound Latitude:")
latitude_upper_label.pack()
latitude_upper_entry = tk.Entry(root)
latitude_upper_entry.pack()


longitude_lower_label = tk.Label(root, text="Lower bound Longitude:")
longitude_lower_label.pack()
longitude_lower_entry = tk.Entry(root)
longitude_lower_entry.pack()

longitude_upper_label = tk.Label(root, text="Upper bound Longitude:")
longitude_upper_label.pack()
longitude_upper_entry = tk.Entry(root)
longitude_upper_entry.pack()

# Create a button to initiate the search
button = tk.Button(root, text="Search", command=search_data)
button.pack()

#add a quit button:
quit_button = tk.Button(root, text="Quit", command=root.quit)
quit_button.pack()

root.mainloop()

