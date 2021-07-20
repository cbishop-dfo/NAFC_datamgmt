# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 16:17:34 2019

@author: BishopC
"""

import datetime as dt
import numpy as np # import numpy library as np
import pandas as pd
import geopy.distance #for distance calculation
#import matplotlib.pyplot as plt

# numerical data file
filename="79001.bot" #move towards taking filename as input in future version.

#data = np.loadtxt(filename,skiprows=4)
#data=np.genfromtxt(filename, delimiter=' ', usecols=[0,1,2,3]) #numpy seems to have issues with file formating of AVG file

data=pd.read_csv(filename, sep=',', skiprows=0) # Pandas loads the AVG file just fine
#print(data)

#first check, see if all Cruise Numbers are the same

number_unique_cruise=data['Cruise_number'].unique()
if number_unique_cruise.shape[0]>1:
    print("more than 1 unique cruise number detected, please check data")
else:
    print("only 1 cruise number detected, good to go...")

#more needed here to identify which entries are out of line, if any...

#end first check

#second check, compute ship velocity and see if it exceeds a certain value, say 10kts
length=data.shape[0]

#initialize some variables:    
n=0  
ranges=[] 
velocity=[]
tdelta_all=[]
while n<(length-1):
     lat1=data.at[n,'latitude']
     lat2=data.at[n+1,'latitude']
     lon1=data.at[n,'longitude']
     lon2=data.at[n+1,'longitude']
     
     #perform distance calc
     
     coords_1=(lat1,lon1)
     coords_2=(lat2,lon2)
     ranges.append(geopy.distance.geodesic(coords_1, coords_2).m)
     
     #get time delta between entries:
     
     dates1=dt.datetime.strptime(data.at[n,'Date'],'%Y-%m-%d').date() #get the date as a string and convert to datetime object
     times1=dt.datetime.strptime(data.at[n,'Time'],'%H:%M:%S').time() #get the time as a string and convert to datetime object
     dt_tm1=dt.datetime.combine(dates1,times1) #combine date and time
     
     dates2=dt.datetime.strptime(data.at[n+1,'Date'],'%Y-%m-%d').date() #get the date as a string and convert to datetime object
     times2=dt.datetime.strptime(data.at[n+1,'Time'],'%H:%M:%S').time() #get the time as a string and convert to datetime object
     dt_tm2=dt.datetime.combine(dates2,times2) #combine date and time
          
     tdelta = (dt_tm2-dt_tm1).total_seconds() #get the delta_time in seconds
     tdelta_all.append(tdelta)
    #get ship velocity: distance/time
     velocity.append((ranges[n]/tdelta)*1.94384) #this should convert velocity from meters per second to knots
     if velocity[n]>12:
         print("Velocity greater than 14kts, check entries %d and %d" % (n,n+1))
     
     #interate through n samples:
     n=n+1
     
#end second check

#third check: Check that all SHIP and TRIP are the same in SHPTRPSTN: 


number_unique_shptrp=data['ShTrpStn'].unique()
if number_unique_cruise.shape[0]>1:
    print("more than 1 unique SHPTRPSTN identifer detected, please check data")
else:
    print("only 1 unique SHPTRPSTN number detected, good to go...")


#more needed here to identify which entries are out of line, if any...
#end third check
    
#fourth check: check stickers, should always be increasing in this file format (i think?)
n=1
while n<(length-1):
    if data.at[n,'Stickr']<data.at[n-1,'Stickr']:
        print("Stickr values should be decreasing, check entries %d through %d" % (n-1,n+1))
    
    #else:
        #print("Looks good")
        
    n=n+1
    
#end fourth check
    
#fifth check:
    
print("Now we perform range checks:")
print("")
print("The T090C data ranges from %f to %f" % (data['T090C'].min() ,data['T090C'].max() ) )
print("")
print("The T190C data ranges from %f to %f" % (data['T190C'].min() ,data['T190C'].max() ) )
print("")
print("The C0S/m data ranges from %f to %f" % (data['C0S/m'].min() ,data['C0S/m'].max() ) )
print("")
print("The C1S/m  data ranges from %f to %f" % (data['C1S/m'].min() ,data['C1S/m'].max() ) )
print("")
print("The Sbeox0V data ranges from %f to %f" % (data['Sbeox0V'].min() ,data['Sbeox0V'].max() ) )
print("")
print("The Sbeox1V data ranges from %f to %f" % (data['Sbeox1V'].min() ,data['Sbeox1V'].max() ) )
print("")
print("The pH data ranges from %f to %f" % (data['Ph'].min() ,data['Ph'].max() ) )
print("")
print("The Sbeox0V data ranges from %f to %f" % (data['Sbeox0V'].min() ,data['Sbeox0V'].max() ) )
print("")
print("The Sbeox1V data ranges from %f to %f" % (data['Sbeox1V'].min() ,data['Sbeox1V'].max() ) )
print("")
print("The FlECO-AFL  data ranges from %f to %f" % (data['FlECO-AFL'].min() ,data['FlECO-AFL'].max() ) )
print("")
print("The WetCDOM data ranges from %f to %f" % (data['WetCDOM'].min() ,data['WetCDOM'].max() ) )
print("")
print("The Par/sat/log data ranges from %f to %f" % (data['Par/sat/log'].min() ,data['Par/sat/log'].max() ) )
print("")
print("The CStarAt0 data ranges from %f to %f" % (data['CStarAt0'].min() ,data['CStarAt0'].max() ) )
print("")
print("The CStarTr0  data ranges from %f to %f" % (data['CStarTr0'].min() ,data['CStarTr0'].max() ) )
print("")
print("The Sal00 data ranges from %f to %f" % (data['Sal00'].min() ,data['Sal00'].max() ) )
print("")
print("The Sal11 data ranges from %f to %f" % (data['Sal11'].min() ,data['Sal11'].max() ) )
print("")
print("The Sigma-t00  data ranges from %f to %f" % (data['Sigma-t00'].min() ,data['Sigma-t00'].max() ) )
print("")
print("The Sigma-t11 data ranges from %f to %f" % (data['Sigma-t11'].min() ,data['Sigma-t11'].max() ) )
print("")
print("The Sbeox0ML/L data ranges from %f to %f" % (data['Sbeox0ML/L'].min() ,data['Sbeox0ML/L'].max() ) )
print("")
print("The Sbeox1ML/L data ranges from %f to %f" % (data['Sbeox1ML/L'].min() ,data['Sbeox1ML/L'].max() ) )
print("")
print("The OxsolML/L  data ranges from %f to %f" % (data['OxsolML/L'].min() ,data['OxsolML/L'].max() ) )
print("")
print("The Sbeox0PS data ranges from %f to %f" % (data['Sbeox0PS'].min() ,data['Sbeox0PS'].max() ) )
print("")
print("The Sbeox1PS data ranges from %f to %f" % (data['Sbeox1PS'].min() ,data['Sbeox1PS'].max() ) )
