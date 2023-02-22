# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:07:24 2023

@author: BISHOPC
"""
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
