__author__ = 'holdenje'

#!/usr/bin/env python

'''
Creates a header list of the met data to be used with the oxycalibration and master bottle file creation
'''

####################################################################################
#import the necessary modules
####################################################################################
#from mpl_toolkits.basemap import Basemap
#import xlsxwriter
import os
import glob
#import re
#import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width',1000)

##############################################
#ask for the working directory
##############################################

#shiptrip = raw_input('Enter the shiptrip number:')
shiptrip = "20118"
#direc = "C:/ctd/2015_trips/" + shiptrip + "/CTDDATA"
direc = "C:/ctd/2018_trips/" + shiptrip + "/CTDDATA"
os.chdir(direc)

savefilename = shiptrip + "_headers.txt"
headerfile = (os.path.join(direc,savefilename))
f = open(headerfile,'a')
for files in sorted(glob.glob('./*.[Dd][0-9][0-9]')):
    print(files)
    #Read in the data
    myfile = open(files)
    str1 = myfile.read()
    splitstr = str1.split('\n')
    hdr2 = splitstr[3]
    print(hdr2)
    f.write(str(hdr2) + '\n')


f.close()