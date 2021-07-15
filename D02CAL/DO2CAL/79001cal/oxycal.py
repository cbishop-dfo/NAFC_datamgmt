#!/usr/bin/env python

from __future__ import print_function

'''
Created on 2015-08-25 by Jennifer Holden
@author: holdenje

loads the *.bot and *_mean02.txt files and manipulates the data

Notes:
The deprecation warnings have been turned off
I needed to install xlsxwriter for the pandas to_excel function to work

IMPORTANT:
As of 11/05/2018, this is the version of this program that I run. In order to run this program, you need to create a directory,
and copy the following files into it:
-<shiptrip>.bot (this may need to be re-run if the last casts aren't already included. If so, I use MobaXterm to navigate
 to the trip directory, then re-run bottle32.exe, which is usually in the BIN/ directory.
 EX: BIN/bottle32.exe 15011.BOT *.btl from within the trip directory)
-<ship><trip>_meanO2.txt (should be in the OXYGEN folder on the trip CD, should be ex, TEL185_meanO2.txt)
-oxy_instr_list.txt (This file can be created by running C:/ctd/misc_scripts/oxycal_createsbe_instr_list.sh in the trip directory.
 The .sh also creates ListInstrumentsUsed.txt, which you don't need). I'm currently running this program though MobaXterm
-<shiptrip>_headers.txt (the met header file. Can be created by running MetData_CreateHeaderFile.py in the trip directory"

!!!!!!!!!!!!!!!FIX!!!!!!!!!!!!!!!!!!!!
There were band-aids added to continue running with the new bot file format. This script doesn't read the old bottle files at the moment
The original bot file has a 2 line header and was space separated
The new bot file is comma separated, has a one line header and is missing the calculated sdv channels. Currently adding columns
of NaNs as a temporary measure to accomadate the sdv channels.
The map plotting portion is currently not working - it was broken during the conversion from Python2.7 to Python3. This should be
a minor fix.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


'''

####################################################################################
#import the necessary modules
####################################################################################
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message="Using default event loop")
#from mpl_toolkits.basemap import Basemap
#import Basemap



import xlsxwriter
#import math
import os
os.environ['PROJ_LIB'] = r'c:\Users\BishopC\AppData\Local\Continuum\anaconda3\Library\share'
from mpl_toolkits.basemap import Basemap

#import time
#import Tkinter, tkFileDialog
import re
#import sys
#import numpy as np
#import matplotlib.pyplot as plt
from pylab import *
import pandas as pd
#from openpyxl import load_workbook
##pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width',1000)
#import regres #this is just the scipy.stats.linregress function. I just couldn't get scipy to load
from matplotlib.widgets import RectangleSelector
from pylab import rcParams
from scipy import stats


###########################
#add the rectangle selector
###########################

def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    global x1, x2, y1, y2
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    global updateflag
    updateflag = True
    #close()

def toggle_selector(event):
    print (' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print (' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print (' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)

##############################################
#ask for the working directory
##############################################
#root = Tkinter.Tk()
#root.withdraw()
#direc = tkFileDialog.askdirectory(initialdir="C:\ctd\DO2CAL",title='Please select a directory')
#direc = "C:\ctd\DO2CAL\python_sample"
#direc = "C:\ctd\DO2CAL\python_sample"
shiptrip = "79001"
direc = "C:/ctd/DO2CAL/"+shiptrip+"cal"
os.chdir(direc)
#root.destroy()

#shiptrip = raw_input('Enter the shiptrip number:')

shipnum = shiptrip[0:2]
trip = shiptrip[2:5]
if shipnum == "39":
    ship = "tel"
    lship = "Teleost"
elif shipnum == "20":
    ship = "hud"
    lship = "Hudson"
elif shipnum == "15":
    ship = "spec"
    lship = "Specials"
elif shipnum == "79":
    ship = "coo"
    lship = "JamesCook"    

#check for presence of *.bot file and *_mean02.txt file
check_bot = os.path.isfile(shiptrip+'.bot')
if check_bot == False:
    print("please move the *.bot file to the working directory")
    sys.exit()
check_meano2 = os.path.isfile(ship+trip+"_meanO2.txt")
if check_meano2 == False:
    print("please move the *_meanO2.txt to the working directory")
    sys.exit()
check_instrlist = os.path.isfile("oxy_instr_list.txt")
if check_instrlist == False:
    print("please move the oxy_instr_list.txt to the working directory. This file can be created by running C:/ctd/misc_scripts/oxycal_createsbe_instr_list.sh in the trip directory (creates this file plus another called ListInstrumentsUsed.txt, which you don't need)")
    sys.exit()
check_hdrlist = os.path.isfile(shiptrip+"_headers.txt")
if check_hdrlist == False:
    print("please move the met header file (shiptrip_headers.txt) to the working directory. This file can be created by running MetData_CreateHeaderFile.py in the trip directory")
    sys.exit()

'''
##################################### FIX THIS! ############################################################################################
########################################################################removed to account for the change in bot file (space delim to comma)
#load the .bot file
with open(shiptrip+'.bot') as fp:
    lcou = 0
    botdict = {};
    for line in fp:
        lcou = lcou+1
        #print(line)
        if lcou == 1:
            varsplit = re.split('\s+',line.rstrip().lstrip())
        elif lcou == 2:
            hdr2split = re.split('\s+',line.rstrip().lstrip())
        elif lcou > 2: # and lcou < 20:
            #print(line)
            numsplit = re.split('\s+',line.rstrip().lstrip())
            while len(numsplit) < len(varsplit):
                numsplit.append('NaN')
            for i in range(0, len(varsplit)):
                if varsplit[i] not in botdict:
                    botdict[varsplit[i]] = [(numsplit[i])]
                else:
                    botdict[varsplit[i]].append((numsplit[i]))
print(botdict)
'''

#load the .bot file
with open(shiptrip+'.bot') as fp:
    lcou = 0
    botdict = {};
    for line in fp:
        lcou = lcou+1
        #print(lcou, line)
        if lcou == 1:
            varsplit = re.split(',', line.rstrip().lstrip())
        elif lcou > 1:
            #print(line)
            numsplit = re.split(',',line.rstrip().lstrip())
            while len(numsplit) < len(varsplit):
                numsplit.append('NaN')
            for i in range(0, len(varsplit)):
                if varsplit[i] not in botdict:
                    botdict[varsplit[i]] = [(numsplit[i])]
                else:
                    botdict[varsplit[i]].append((numsplit[i]))

#This was added 20190218 as a band-aid for the new format of the bottle file. Need to ask Gary if the sdv channels are actually needed at all.
if 'Sal00_sdv' not in botdict.keys():
    botdict['Sal00_sdv'] = len(botdict['Sal00']) * np.nan
    botdict['Sal11_sdv'] = len(botdict['Sal11']) * np.nan
    botdict['Sigma-t00_sdv'] = len(botdict['Sigma-t00']) * np.nan
    botdict['Sigma-t11_sdv'] = len(botdict['Sigma-t11']) * np.nan
    botdict['Sbeox0ML/L_sdv'] = len(botdict['Sbeox0ML/L']) * np.nan
    botdict['Sbeox1ML/L_sdv'] = len(botdict['Sbeox1ML/L']) * np.nan
    botdict['OxsolML/L_sdv'] = len(botdict['OxsolML/L']) * np.nan
    botdict['Sbeox0PS_sdv'] = len(botdict['Sbeox0PS']) * np.nan
    botdict['Sbeox1PS_sdv'] = len(botdict['Sbeox1PS']) * np.nan

#accommodate the fact that Ph and Par sometimes show up with changing variable names
if 'Par/log' in botdict.keys():
    botdict['Par/lo'] = botdict.pop('Par/log')
    botdict['Par/lo_sdv'] = botdict.pop('Par/log_sdv')
if 'Ph' in botdict.keys():
    botdict['P'] = botdict.pop('Ph')
    botdict['P_sdv'] = botdict.pop('Ph_sdv')

if 'Par/sat/log' in botdict.keys():
    botdict['Par/lo'] = botdict.pop('Par/sat/log')
    botdict['Par/lo_sdv'] = botdict.pop('Par/sat/log_sdv')
if 'CStarTr0' in botdict.keys():
    botdict['CStarTr'] = botdict.pop('CStarTr0')
    botdict['CStarTr_sdv'] = botdict.pop('CStarTr0_sdv')

#load the *_meanO2.txt file
with open(ship+trip+"_meanO2.txt") as fp:
    meano2dict = {}
    lcou = 0
    for line in fp:
        lcou = lcou+1
        if lcou > 9:
            numsplit = re.split(',',line.rstrip().lstrip())
            for i in range(0, len(varsplit)):
                if not numsplit[i]:
                    numsplit[i] = "NaN"
                if varsplit[i] not in meano2dict:
                    meano2dict[varsplit[i]] = [(numsplit[i])]
                else:
                    if not numsplit[i]:
                        meano2dict[varsplit[i]].append(("NaN"))
                    else:
                        meano2dict[varsplit[i]].append((numsplit[i]))

        if lcou == 9:
            varsplit = re.split(',',line.rstrip().lstrip())
    if varsplit[0] != "Sample":
        print(ship, trip, "_mean02.txt has the wrong number of header lines!")
        sys.exit()

#load the instrument list file
with open("oxy_instr_list.txt") as fp:
    instdict = {}
    lcou = 0
    for line in fp:
        lcou = lcou+1
        if lcou > 1:
            numsplit = re.split(",", line.rstrip().lstrip())
            for i in range(0, len(varsplit)):
                if varsplit[i] not in instdict:
                    instdict[varsplit[i]] = [(numsplit[i])]
                else:
                    if not numsplit[i]:
                        instdict[varsplit[i]].append(("NaN"))
                    else:
                        instdict[varsplit[i]].append((numsplit[i]))
        if lcou == 1:
            varsplit = re.split(',',line.rstrip().lstrip())

    if varsplit[0] != "Filename":
        print(ship, trip, "oxy_instr_list.txt has the wrong number of header lines!")
        sys.exit()


#indices of the shared sticker numbers
shared_stickers = list(set(botdict["Stickr"]) & set(meano2dict["Sample"]))
indices = [i for (i,x) in enumerate(botdict["Stickr"]) if x in set(meano2dict["Sample"]).intersection(botdict["Stickr"])]
oxystations = []
for i in indices:
    oxystations.append(botdict["Station-ID"][i])
print("The stations where Oxygen samples were collected are: ")
osdict = {}
for stat in np.unique(oxystations):
    sval = re.split('-',stat)
    if sval[0] not in osdict:
        osdict[sval[0]] = [sval[1]]
    else:
        osdict[sval[0]].append(sval[1])

for k in osdict.keys():
    print(k, ":", ", ".join(osdict.get(k)))
print(" ")
check_stations = "y" #raw_input("Is this list of stations complete? (y/n)    ")
if check_stations != "y":
    print(" ")
    print("You must confirm that the sticker numbers in the input files are correct before continuing!")
    print("Exiting")
    sys.exit()

#add the data to a dataframe using pandas
botdf = pd.DataFrame(botdict)
mo2df = pd.DataFrame(meano2dict)
insdf = pd.DataFrame(instdict)
#(len(botdf), len(mo2df), len(insdf))

#**********************************************************************************************************FIX
#Another band-aid due to the new bottle file format. Check to see if the degrees longitude is positive - if so, multiply by -1
if float(botdf['lonD'][1]) > 0:
    botdf['lonD'] = botdf['lonD'].astype(float)*(-1)

oxysamples1 = pd.merge(botdf, mo2df, left_on='Stickr', right_on='Sample', how='inner')
oxysamples = pd.merge(oxysamples1,insdf,left_on='ShTrpStn', right_on='Filename', how='inner')
if len(oxysamples1) != len(oxysamples):
    print('There are not the same number of samples in (botdf + mo2df) as there are in (botdf + mo2df + instdf). Probably a typo in the bottle file')
    #print botdf['ShTrpStn']
    print(oxysamples1['ShTrpStn'].tolist())
    print("")
    print(oxysamples['ShTrpStn'].tolist())
    #print("")
    #print(oxysamples[['Filename','ShTrpStn']])
    sys.exit()

print(" ")
typoflag=False
teststn = 0
for sts in range(len(botdf['ShTrpStn'])):
    #print int(botdf['ShTrpStn'][sts][5:8]), int(teststn)
    if botdf['ShTrpStn'][sts][0:5] != shiptrip:
        typoflag=True
        print("Typo in bottle file: ", botdf['Station-ID'][sts], botdf['ShTrpStn'][sts])
        pause(2)
    if int(botdf['ShTrpStn'][sts][5:8]) < int(teststn):
        typoflag=True
        print("Typo in bottle file: ", botdf['Station-ID'][sts], botdf['ShTrpStn'][sts])
        print("...typo is actually most likely in ", botdf['Station-ID'][sts-1], botdf['ShTrpStn'][sts-1])
    teststn = int(botdf['ShTrpStn'][sts][5:8])

teststn = 0
for sts in range(len(insdf['Filename'])):
    if insdf['Filename'][sts][0:5] != shiptrip:
        typoflag=True
        print("Typo in inst file: ", insdf['Filename'][sts])
        pause(2)
    if int(insdf['Filename'][sts][5:8]) < int(teststn):
        typoflag=True
        print("Typo in inst file: ", insdf['Filename'][sts])
        print("...typo is actually most likely in ", insdf['Filename'][sts-1], ")")
    teststn = int(insdf['Filename'][sts][5:8])

if typoflag==True:
    sys.exit()

#start the master bottle file
startmasterdf = pd.merge(botdf,insdf,left_on='ShTrpStn', right_on='Filename', how='inner')

#this line pre-defines the column so that I don't get a key error. There should be a better way!
oxysamples["WINKLER"] = (oxysamples["Rep_1(ml/l)"].astype(float)+oxysamples["Rep_2(ml/l)"].astype(float))/2
#add in the values for if one of the reps are a NaN
for da in range(0,len(oxysamples["Rep_1(ml/l)"])):
    ov1 = float(oxysamples["Rep_1(ml/l)"][da])
    ov2 = float(oxysamples["Rep_2(ml/l)"][da])
    if (math.isnan(ov1) == False) & (math.isnan(ov2) == False):
        oxysamples["WINKLER"].set_value(da,((ov1+ov2)/2))
    elif (math.isnan(ov1) == True) & (math.isnan(ov2) == False):
        oxysamples["WINKLER"].set_value(da,ov2)
    elif (math.isnan(ov1) == False) & (math.isnan(ov2) == True):
        oxysamples["WINKLER"].set_value(da,ov1)

#add the difference column
oxysamples["WINKLER-DIFF"] = abs(oxysamples["Rep_1(ml/l)"].astype(float)-oxysamples["Rep_2(ml/l)"].astype(float))

#add section names
oxysamples["section"] = oxysamples["Station-ID"]
for v in oxysamples.index:
    se = re.split('-',oxysamples["Station-ID"][v])[0]
    oxysamples["section"].set_value(v,se)

#Remove rows where WINKLER = NaN
oxysamples = oxysamples[pd.notnull(oxysamples["WINKLER"])]

#print failed_titrations##############################################################################################
print("These titrations have rep averages outside the range of 2-8 and/or differences of >0.2:")
failed_titrations = oxysamples.loc[(oxysamples["WINKLER"] > 9) | (oxysamples["WINKLER"] < 2) | (oxysamples["WINKLER-DIFF"] > 0.2),["Sample","Station-ID","Sbeox0ML/L","WINKLER","WINKLER-DIFF"]]
print(failed_titrations)

###############################################################################
#This is probably where I should loop back to
###############################################################################

#Run though sensor numbers
sens = np.unique(oxysamples["PrimOSens"].append(oxysamples["SecOSens"]))
regresdict = {}
origoxysamples = oxysamples
plotnamelist = []
histnamelist = []
sectionregres = []
sregres = {}
updateflag = False
for s in sens:
    cancelflag = False
    doneflag = False
    origflag = True
    x1 = 0; x2 = 0; y1 = 0; y2 = 0
    oxysamples = origoxysamples
    rpts = []
    while doneflag == False:
        Sbeox = []; Wink = []; OldSall = []; WS = []; scid = []
        for l in oxysamples.index:
            if oxysamples["PrimOSens"][l] == s:
                Sbeox.append(float(oxysamples["Sbeox0ML/L"][l]))
                Wink.append(float(oxysamples["WINKLER"][l]))
                OldSall.append(float(oxysamples["PrimSOC"][l]))
                scid.append((oxysamples["section"][l]))
                WS.append(float(oxysamples["WINKLER"][l])/float(oxysamples["Sbeox0ML/L"][l]))
            elif oxysamples["SecOSens"][l] == s:
                Sbeox.append(float(oxysamples["Sbeox1ML/L"][l]))
                Wink.append(float(oxysamples["WINKLER"][l]))
                OldSall.append(float(oxysamples["SecSOC"][l]))
                scid.append((oxysamples["section"][l]))
                WS.append(float(oxysamples["WINKLER"][l])/float(oxysamples["Sbeox1ML/L"][l]))
            else:
                continue

        OldSoc = np.unique(OldSall)
        if len(OldSoc) != 1:
            print("Error!")
            print("You have too many OldSOC values for", s)
            print("Check the sbe files for SOC values of", OldSoc)
            exit()

        #calculate NewSOC
        Newsoc = float("{0:.4f}".format(np.average(np.array(WS))*float(OldSoc[0])))

        #linear regression
        slope, intercept, r_value, pvalue, std_err = stats.linregress(np.array(Sbeox),np.array(Wink))
        yp = polyval([slope,intercept],np.array(Sbeox))
        #print "y =", "{0:.4f}".format(slope), "x +", "{0:.4f}".format(intercept) + ", R^2 = " + "{0:.4f}".format(r_value**2)

        #plot
        rcParams['figure.figsize'] = 15, 10
        fig = plt.figure(1)
        fig.subplots_adjust(left=0.3)#18) #leave room for buttons
        atitle = lship + " " + trip + " SBE-43 S/N " + s + " DO2 Sensor Calibration \n (All Sections)"
        legap = "y =" + "{0:.4f}".format(slope) + "x +" + "{0:.4f}".format(intercept) + "\n$R^2$ = " + "{0:.4f}".format(r_value**2)
        #plt.ion()
        ax = fig.add_subplot(1,1,1)
        ax.plot(np.array(Sbeox),yp,'k',label=legap)
        #xminval = np.minimum(0,np.min(map(float,Sbeox))-1)
        #yminval = np.minimum(0,np.min(Wink)-1)
        xminval = np.minimum(np.min(Wink)-1,np.min(np.array(Sbeox))-1)
        yminval = np.minimum(np.min(Wink)-1,np.min(np.array(Sbeox))-1)
        plt.xlim(xminval,np.max(np.array(Sbeox))+1)
        plt.ylim(yminval,np.max(Wink)+1)
        #plt.xlim(0,np.max(map(float,Sbeox))+1) #0.5)
        #plt.ylim(0,np.max(Wink)+1) #0.5)
        plt.xlabel("Probe DO2 (ml/l)",fontsize=14)
        plt.ylabel("Bottle DO2 (ml/l)",fontsize=14)
        plt.grid(True)
        plt.title(atitle,fontsize=16)
        if origflag == False:
            plt.plot(origSbeox,origWink,'rx',markersize=5,mew=1.5,label="Unused Samples")
        #Individual Sections
        templist = []
        templist.append([s, "ALL", slope, intercept, r_value**2])
        #templist = []
        for uscid in np.unique(scid):
            scind = [i for (i,x) in enumerate(scid) if x in uscid]
            Wuse = [Wink[i] for i in scind]
            Suse = [np.array(Sbeox)[i] for i in scind]
            legap2 = uscid
            plt.plot(Suse,Wuse,'o',mec='k',label=legap2,markersize=8)
        '''
        tslope, tintercept, tr_value, tstd_err = regres.linregress(map(float,Suse),Wuse)
        templist.append([s, uscid, tslope, tintercept, tr_value**2])
        ypp = polyval([tslope, tintercept], Suse)
        ax.plot(Suse, ypp, 'k', label=legap)
        '''

        #legend
        rcParams['legend.loc'] = 'lower right' #'best'
        plt.legend(numpoints=1, fancybox=True)

        ################################
        #draw the rectangle
        ################################
        # drawtype is 'box' or 'line' or 'none'
        current_ax=plt.gca() #ax
        toggle_selector.RS = RectangleSelector(current_ax, line_select_callback, drawtype='box', useblit=True, button=[1,3], minspanx=5, minspany=5, spancoords='pixels')
        plt.connect('key_press_event', toggle_selector)

        ##############################
        #add the buttons
        ##############################
        def donebutton(event):
            global doneflag
            doneflag = True
            if "inst" not in regresdict:
                regresdict["inst"] = [s]
                regresdict["slope"] = [slope]
                regresdict["intercept"] = [intercept]
                regresdict["NewSOC"] = [Newsoc]
                regresdict["OldSOC"] = [float(OldSoc[0])]
                regresdict["R2"] = [r_value**2]
            elif s not in regresdict["inst"]:
                regresdict["inst"].append(str(s))
                regresdict["slope"].append(float(slope))
                regresdict["intercept"].append(float(intercept))
                regresdict["NewSOC"].append(Newsoc)
                regresdict["OldSOC"].append(float(OldSoc[0]))
                regresdict["R2"].append(float(r_value**2))

            plotname = shiptrip + "_S" + s
            extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            plt.savefig(os.path.join(direc,plotname),bbox_inches=extent.expanded(1.1, 1.2))
            plotnamelist.append(plotname+'.png')
            close()

            #compile the regression stats by section
            sectionregres.append(templist)
            class listwrap:
                def __init__(self, lis):
                    self._list = lis
                def __getitem__(self, dex):
                    i,j = dex
                    return self._list[i][j]
            n = []; sl = []; ins = []; intc = []; r2 = [];
            l = listwrap(templist)
            for i in range(0,len(templist)):
                n.append(l[i,1])
                sl.append(l[i,2])
                ins.append(l[i,0])
                intc.append(l[i,3])
                r2.append(float(l[i,4])**2)
            #make the histogram
            data = {'Slopes': pd.Series(sl, index=n), 'Intercepts': pd.Series(intc, index=n), '$R^2$': pd.Series(r2, index=n)}
            df = pd.DataFrame(data)

            if len(n) < 4:
                pw = 3.5*len(n)
            else:
                pw = 2.5*len(n)
            df[['Slopes','Intercepts','$R^2$']].plot(kind='bar',stacked = False, color = ['navy','grey','red'],figsize=(pw,10),fontsize=12)
            title(lship + " " + trip + " SBE-43 S/N " + s + ' DO2 Sensor Calibration \n Regression by section', fontsize=16)
            axhline(0, color=[0.3,0.3,0.3])
            histname = shiptrip + "_S" + s + "_hist"
            plt.savefig(os.path.join(direc,histname),bbox_inches='tight')
            histnamelist.append(histname+'.png')
            plt.ion()
            plt.show()
            plt.pause(0.005)
            plt.close()
            plt.ioff()

        def cancelbutton(event):
            plt.close()
            global cancelflag
            cancelflag = True

        #add the buttons to the plot
        axcancel = plt.axes([0.03, 0.26, 0.16, 0.10])
        bcancel = Button(axcancel, 'Cancel')
        bcancel.on_clicked(cancelbutton)
        axdone = plt.axes([0.03, 0.1, 0.16, 0.10])
        bdone = Button(axdone, 'Done\n (Save Changes)')
        bdone.on_clicked(donebutton)

        #add a textbox to show deleted samples
        if origflag == False:
            rptslist = [item for sublist in rpts for item in sublist]
            if len(rptslist) > 20:
                remlabel = "Too many samples \nhave been removed \nto print all Sample IDs. \nConfirm titration data!"
            else:
                remlabel = str("Unused Samples:\n" + '\n'.join(rptslist))
            #plt.text(0.05, 8, remlabel,verticalalignment='top',bbox=dict(facecolor='white',alpha=0.5,pad=20),fontsize=14)
            plt.text(1.79, 0.25, remlabel,verticalalignment='bottom',bbox=dict(facecolor='white',alpha=0.5,pad=20),fontsize=14)

        #show the plot
        plt.ion()
        if origflag == True:
            plt.show()
        else:
            plt.draw()

        while not updateflag and not doneflag and not cancelflag:
            plt.pause(0.00005)
        if cancelflag:
            exit()
        updateflag = False
        plt.clf()

        #this bit saves out the original data
        if origflag == True:
            origSbeox = Sbeox
            origWink = Wink
        origflag = False

        #define the boxes boundaries
        bot = min(y1, y2); top = max(y1, y2)
        lef = min(x1, x2); rgt = max(x1, x2)

        ## This bit picks which indices should end up in the 'keep' dataframe ##
        #find all indices of points in box regardless of instrument

        #There's a problem here - The following code assumes that an individual oxygen sensor will either always be primary
        #or always secondary. For example, on 39159, two instruments were used (S1146 with oxy sensors

        if s in np.unique(oxysamples["PrimOSens"]):
            idx = oxysamples[(oxysamples["Sbeox0ML/L"].astype(float) < rgt) & (oxysamples["Sbeox0ML/L"].astype(float) > lef) & (oxysamples["WINKLER"].astype(float) < top) & (oxysamples["WINKLER"].astype(float) > bot)].index.tolist()
        elif s in np.unique(oxysamples["SecOSens"]):
            idx = oxysamples[(oxysamples["Sbeox1ML/L"].astype(float) < rgt) & (oxysamples["Sbeox1ML/L"].astype(float) > lef) & (oxysamples["WINKLER"].astype(float) < top) & (oxysamples["WINKLER"].astype(float) > bot)].index.tolist()
        #find all points in the whole df that are not in the points to lose
        keepidx1 = set(list(oxysamples.index)).difference(idx)
        #find all the points with the right instrument number
        keepidx2 = oxysamples[(oxysamples["PrimOSens"] == str(s)) | (str(s) == oxysamples["SecOSens"])].index.tolist()
        #find the points with the right instrument number that should be kept
        keepidx = set(keepidx1).intersection(keepidx2)
        #find the points with the right instrument number that should be tossed
        ptstoremove = set(idx).intersection(keepidx2)
        #if there are any points to remove, add their sample numbers to a list to print on the plot
        if len(ptstoremove) != 0:
            rpts.append(list(oxysamples.loc[ptstoremove]["Sample"].values))
        #rewrite the df so that it only contains the points to keep
        oxysamples = oxysamples.loc[keepidx]


##############################################################################################
#This stuff should be after the loop. It needs to use the final values for slope and intercept
##############################################################################################

#print out a table that has the calculated parameters in it
print(" ")
print("inst", "\t", "slope", "\t", "int", "\t", "R^2", "\t", "OldSOC", "\t", "NewSOC")
for bi in range(0,len(regresdict["inst"])):
    print(regresdict["inst"][bi], "\t", "{0:.4f}".format(regresdict["slope"][bi]), "\t", "{0:.4f}".format(regresdict["intercept"][bi]), "\t", "{0:.2f}".format(regresdict["R2"][bi]), "\t", "{0:.4f}".format(regresdict["OldSOC"][bi]), "\t", "{0:.4f}".format(regresdict["NewSOC"][bi]))


print(" ")
print("creating and saving master bottle file")
## write out the master bottle file ##
masterdf = pd.DataFrame(index=startmasterdf.index, columns=['STATION NAME','DATE (yyyy-mm-dd)','TIME UTC','ShTrpStn FILENAME','STICKER NUMBER','LATITUDE DEGREES','LATITUDE MINUTES','LONGITUDE DEGREES','LONGITUDE MINUTES','PRESSURE','T-90 (oC)','SALINITY','SIGMA-T','DO2 SATURATION','FIECO-AFL','PAR','PH','DO2','DO2 %SATURATION','WetCDOM','CStarAt0','CStarAt0_sdv','CStarTr','CStarTr_sdv'])
#print(startmasterdf)
for smd in startmasterdf.index:
    v = regresdict["inst"].index(startmasterdf["PrimOSens"][smd])
    slp = float(regresdict["slope"][v])
    intt = float(regresdict["intercept"][v])
    masterdf["STATION NAME"][smd] = startmasterdf["Station-ID"][smd]
    masterdf["DATE (yyyy-mm-dd)"][smd] = startmasterdf["Date"][smd]
    masterdf["TIME UTC"][smd] = startmasterdf["Time"][smd]
    masterdf["ShTrpStn FILENAME"][smd] = startmasterdf["ShTrpStn"][smd]
    masterdf["STICKER NUMBER"][smd] = float(startmasterdf["Stickr"][smd])
    masterdf["LATITUDE DEGREES"][smd] = float(startmasterdf["latD"][smd])
    masterdf["LATITUDE MINUTES"][smd] = float(startmasterdf["latM"][smd].strip('N'))
    masterdf["LONGITUDE DEGREES"][smd] = float(startmasterdf["lonD"][smd])
    #masterdf["LONGITUDE DEGREES"][smd] = masterdf["LONGITUDE DEGREES"][smd]*(-1)
    masterdf["LONGITUDE MINUTES"][smd] = float(startmasterdf["lonM"][smd].strip('W'))
    masterdf["PRESSURE"][smd] = float(startmasterdf["PrDM"][smd])
    masterdf["T-90 (oC)"][smd] = float(startmasterdf["T090C"][smd])
    masterdf["SALINITY"][smd] = float(startmasterdf["Sal00"][smd])
    masterdf["SIGMA-T"][smd] = float(startmasterdf["Sigma-t00"][smd])
    masterdf["DO2 SATURATION"][smd] = float(startmasterdf["OxsolML/L"][smd])
    masterdf["DO2"][smd] = float(startmasterdf["Sbeox0ML/L"][smd]) * slp + intt
    masterdf["DO2 %SATURATION"][smd] = (float(masterdf["DO2"][smd])/float(startmasterdf["OxsolML/L"][smd]))*100
    masterdf["FIECO-AFL"][smd] = float(startmasterdf["FlECO-AFL"][smd])
    masterdf["PAR"][smd] = float(startmasterdf["Par/lo"][smd])
    masterdf["PH"][smd] = float(startmasterdf["P"][smd])
    masterdf["CStarAt0"][smd] = float(startmasterdf["CStarAt0"][smd])
    masterdf["CStarTr"][smd] = float(startmasterdf["CStarTr"][smd])
    masterdf["CStarAt0_sdv"][smd] = float(startmasterdf["CStarAt0_sdv"][smd])
    masterdf["CStarTr_sdv"][smd] = float(startmasterdf["CStarTr_sdv"][smd])
    masterdf["WetCDOM"][smd] = float(startmasterdf["WetCDOM"][smd])


'''
if len(botdf) != len(masterdf):
    print " "
    print len(botdf), len(masterdf)
    print "Bottle file and master are different lengths. There's a typo somewhere!"
    testtestdf = pd.merge(masterdf,botdf,left_on='ShTrpStn FILENAME',right_on='ShTrpStn',how='outer')
    print testtestdf
    sys.exit()
'''
# read in the Met data

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

with open(shiptrip+"_headers.txt") as fp:
    winddict = {}; winddict['Filename'] = []; winddict['WindDirection'] = []; winddict['WindSpeed_kts'] = []
    for line in fp:
        #splitstr = line.split('\n')
        #hdr2 = splitstr[3]
        if isfloat(line[0:8])==True:
            winddict['Filename'].append(line[0:8])
        else:
            winddict['Filename'].append(np.nan)
        if isfloat(line[11:13])==True:
            winddict['WindDirection'].append(float(line[11:13]))
        else:
            winddict['WindDirection'].append(np.nan)
        if isfloat(line[14:16])==True:
            winddict['WindSpeed_kts'].append(float(line[14:16]))
        else:
            winddict['WindSpeed_kts'].append(np.nan)

winddf = pd.DataFrame(winddict)
winddf['WindSpeed_m/s'] = np.multiply(0.514444, winddf['WindSpeed_kts'].astype(float))

#print winddf

#duplicates appear in newmasterdf after the following codes: ***WHY???****

#merge the met data with the master bottle file data
masterwinddf = pd.merge(masterdf,winddf,how='left',left_on='ShTrpStn FILENAME',right_on='Filename')
masterwinddf['ShTrpStn FILENAME'] = masterwinddf['ShTrpStn FILENAME'].astype(float)
newmasterdf = masterwinddf.ix[:,['STATION NAME','DATE (yyyy-mm-dd)','TIME UTC','ShTrpStn FILENAME','STICKER NUMBER','LATITUDE DEGREES','LATITUDE MINUTES','LONGITUDE DEGREES','LONGITUDE MINUTES','PRESSURE','T-90 (oC)','SALINITY','SIGMA-T','DO2','DO2 SATURATION','DO2 %SATURATION','FIECO-AFL','PAR','PH','WetCDOM','CStarAt0','CStarTr','WindDirection','WindSpeed_kts','WindSpeed_m/s']]

newmasterdf.drop_duplicates()

#write to the excel file
xlsxfilename = shiptrip + "_master_bottle_file.xlsx"
writer = pd.ExcelWriter(xlsxfilename)
newmasterdf.to_excel(writer,shiptrip,index=False)
botdf.to_excel(writer,'OrigData',index=False)
writer.save()

## Find some summary data ##
mindates = min(masterdf["DATE (yyyy-mm-dd)"])
maxdates = max(masterdf["DATE (yyyy-mm-dd)"])

import time
a = time.strptime(mindates, "%Y-%m-%d")
b = time.strptime(maxdates, "%Y-%m-%d")
if time.strftime("%Y", a) != time.strftime("%Y", b):
    daterang = time.strftime("%B %d, %Y", a) + " - " + time.strftime("%B %d, %Y", b)
else:
    if time.strftime("%B", a) != time.strftime("%B", b):
        daterang = time.strftime("%B", a) + ' ' + time.strftime("%d", a) +' - ' + time.strftime("%B", b) + ' ' + time.strftime("%d", b) + ', ' + time.strftime("%Y", b)
    else:
        daterang = time.strftime("%B", a) + ' ' + time.strftime("%d", a) + '-' + time.strftime("%d", b) + ", " + time.strftime("%Y", b)

mapname = shiptrip + '_stns.png'
#maptest = os.path.isfile(os.path.join(direc,mapname))
#######################################################################Another broken part!!!!!!!!!!!!!!!!!!!!!!!!!!!
maptest = True


#if maptest == False:
if maptest == True:
    print(" ")
    print("create the locations map")
    ## Create the locations map ##
    lats_all = masterdf["LATITUDE DEGREES"].astype(float)+masterdf["LATITUDE MINUTES"].astype(float)/60
    lons_all = masterdf["LONGITUDE DEGREES"].astype(float)-masterdf["LONGITUDE MINUTES"].astype(float)/60
    lats_used = origoxysamples["latD"].astype(float)+origoxysamples["latM"].astype(float)/60
    lons_used = origoxysamples["lonD"].astype(float)-origoxysamples["lonM"].astype(float)/60
    #find the min and max lat and lon to use with plotting
    minlats = min(min(lats_all),min(lats_used))
    maxlats = max(max(lats_all),max(lats_used))
    minlons = min(min(lons_all),min(lons_used))
    maxlons = max(max(lons_all),max(lons_used))
    #Define a projection
    map = Basemap(projection='merc', lat_0 = 57, lon_0 = -135, lat_ts = 57, resolution = 'h', area_thresh = 0.1, llcrnrlon=minlons-12, llcrnrlat=minlats-6.0, urcrnrlon=maxlons+8.0, urcrnrlat=maxlats+10.0)
    #Fill in the map
    map.drawcoastlines()
    map.drawcountries()
    map.fillcontinents(color = 'gray')
    #map.drawmapboundary()
    map.drawparallels(np.arange(10,70,2),labels=[0,1,0,0],linewidth=0) #[left,right,top,bottom]
    map.drawmeridians(np.arange(-100,0,4),labels=[0,0,0,1],linewidth=0)
    #Convert the lat and lon to projection co-ordinates and plot
    x_all,y_all = map(np.array(lons_all), np.array(lats_all))
    map.scatter(x_all, y_all, 60, marker='o', color='b', edgecolors='k', label="Occupied stations")
    x_used,y_used = map(np.array(lons_used), np.array(lats_used))
    map.scatter(x_used, y_used, 60, marker='o', color='r', edgecolors='k',label="Oxygen sample")
    plt.title("Occupied stations for all instruments used during " + shiptrip, fontsize=16)
    plt.legend(numpoints=1)
    #save the figure
    fig1 = plt.gcf()
    #mapname = shiptrip + '_stns.png'
    fig1.savefig(os.path.join(direc,mapname), bbox_inches='tight')
    plt.ioff()
    plt.close()



print(" ")
print("creating and saving the calibration file")
## Print a calibration summary to excel ##
DO2calfilename = shiptrip + "_DO2calibration.xlsx"
workbook = xlsxwriter.Workbook(DO2calfilename, {'nan_inf_to_errors': True})

#write out the summary
summarysheet = workbook.add_worksheet('summary')

summarysheet.write(0,0,'Oxygen Calibration')
summarysheet.write(1,0,'AZMP Survey '+lship+' '+trip)
summarysheet.write(2,0,daterang)
summarysheet.write(4,0,'The following instruments were used:')

row = 5
for k in range(0,len(sens)):
    se = sens[k]
    le = len(startmasterdf.loc[startmasterdf['PrimOSens'] == str(se)])
    le2 = len(startmasterdf.loc[startmasterdf['SecOSens'] == str(se)])
    #print se, le, le2
    summarysheet.write(row,1,se+': '+str(le)+' records as primary and '+str(le2)+' records as secondary')
    row += 1

#write out the occupied stations (osdict)
row += 1
summarysheet.write(row,0,'The following stations were occupied:')
he = osdict.keys()
row += 1
for sect in he:
    statstring = sect + ': ' + ', '.join((osdict[sect]))
    summarysheet.write(row,1,statstring)
    row += 1

#write the regression data
row += 1
summarysheet.write(row,0,'The regression data is:')
ordered_list = ['inst','slope','intercept','R2','OldSOC','NewSOC']
first_row=row+1
for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    summarysheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in regresdict[itm]:
        col = ordered_list.index(itm)
        summarysheet.write(row,col,(val))
        row += 1

#write out the map plot
mapname = shiptrip + '_stns.png'
summarysheet.insert_image('I2',mapname,{'x_scale': 0.5, 'y_scale': 0.5})


#write out the plots
plotssheet = workbook.add_worksheet('plots')
cel = ['B2','B27','B52','B77','B102']
for ii in range(0,len(plotnamelist)):
    plotssheet.insert_image(cel[ii],plotnamelist[ii],{'x_scale': 0.5, 'y_scale': 0.5})

#write out the hist plots
cel = ['J3','J28','J53','J78','J103']
for ii in range(0,len(histnamelist)):
    plotssheet.insert_image(cel[ii],histnamelist[ii],{'x_scale': 0.5, 'y_scale': 0.5})

#convert the dataframe to a dictionary so that it will be easier to write to the excel sheet
masterdict = masterdf.to_dict('list')
mastersheet = workbook.add_worksheet('master bottle file')
first_row=0
#ordered_list = masterdict.keys()
ordered_list = ['STATION NAME','DATE (yyyy-mm-dd)','TIME UTC','ShTrpStn FILENAME','STICKER NUMBER','LATITUDE DEGREES',
                'LATITUDE MINUTES','LONGITUDE DEGREES','LONGITUDE MINUTES','PRESSURE','T-90 (oC)','SALINITY','SIGMA-T',
                'DO2','DO2 SATURATION','DO2 %SATURATION','FIECO-AFL','PAR','PH','WetCDOM','CStarAt0','CStarTr']
for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    mastersheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in masterdict[itm]:
        col = ordered_list.index(itm)
        mastersheet.write(row,col,(val))
        row += 1


datadict = origoxysamples.to_dict('list')

'''
float_ordered_list = ['latM', 'lonM', 'PrDM', 'PrDM_sdv', 'T090C', 'T090C_sdv', 'T190C', 'T190C_sdv', 'C0S/m', 'C0S/m_sdv',
                      'C1S/m', 'C1S/m_sdv', 'Sal00', 'Sal00_sdv', 'Sal11', 'Sal11_sdv', 'Sigma-t00', 'Sigma-t00_sdv', 'Sigma-t11',
                      'Sigma-t11_sdv', 'Sbeox0V', 'Sbeox0V_sdv', 'Sbeox1V', 'Sbeox1V_sdv', 'Sbeox0ML/L', 'Sbeox0ML/L_sdv', 'Sbeox1ML/L',
                      'Sbeox1ML/L_sdv', 'OxsolML/L', 'OxsolML/L_sdv', 'Sbeox0PS', 'Sbeox0PS_sdv', 'Sbeox1PS', 'Sbeox1PS_sdv',
                      'FlECO-AFL', 'FlECO-AFL_sdv', 'Par', 'Par_sdv', 'P', 'P_sdv', '[O2](ml/l)', 'std_[O2](ml/l)', 'Rep_1(ml/l)',
                      'Rep_2(ml/l)', 'PrimSOC', 'SecSOC', 'WINKLER', 'WINKLER-DIFF', 'ShTrpStn', 'Stickr', 'latD', 'lonD', 'Sample', 'Filename', 'Instr', 'PrimOSens', 'SecOSens']
'''

float_ordered_list = ['latM', 'lonM', 'PrDM', 'PrDM_sdv', 'T090C', 'T090C_sdv', 'T190C', 'T190C_sdv', 'C0S/m',
                      'C0S/m_sdv', 'C1S/m', 'C1S/m_sdv', 'Sal00', 'Sal00_sdv', 'Sal11', 'Sal11_sdv', 'Sigma-t00', 'Sigma-t00_sdv',
                      'Sigma-t11', 'Sigma-t11_sdv', 'Sbeox0V', 'Sbeox0V_sdv', 'Sbeox1V', 'Sbeox1V_sdv', 'Sbeox0ML/L',
                      'Sbeox0ML/L_sdv', 'Sbeox1ML/L', 'Sbeox1ML/L_sdv', 'OxsolML/L', 'OxsolML/L_sdv', 'Sbeox0PS', 'Sbeox0PS_sdv', 'Sbeox1PS',
                      'Sbeox1PS_sdv', 'FlECO-AFL', 'FlECO-AFL_sdv', 'Par/lo', 'Par/lo_sdv', 'P', 'P_sdv','WetCDOM','CStarAt0','CStarAt0_sdv','CStarTr','CStarTr_sdv',
                      '[O2](ml/l)', 'std_[O2](ml/l)',
                      'Rep_1(ml/l)', 'Rep_2(ml/l)', 'PrimSOC', 'SecSOC', 'WINKLER', 'WINKLER-DIFF', 'ShTrpStn', 'Stickr', 'latD',
                      'lonD', 'Sample', 'Filename']
for key in float_ordered_list:
    #print datadict[key]
    for idx, val in enumerate(datadict[key]):
        datadict[key][idx] = float(val)

datasheet = workbook.add_worksheet('data')
first_row=0

ordered_list = ['Station-ID','Date','Time','ShTrpStn','Stickr','latD','latM','lonD','lonM','PrDM','PrDM_sdv','T090C','T090C_sdv','T190C','T190C_sdv','C0S/m',
                'C0S/m_sdv','C1S/m','C1S/m_sdv','Sal00','Sal00_sdv','Sal11','Sal11_sdv','Sigma-t00','Sigma-t00_sdv','Sigma-t11','Sigma-t11_sdv','Sbeox0V',
                'Sbeox0V_sdv','Sbeox1V','Sbeox1V_sdv','Sbeox0ML/L','Sbeox0ML/L_sdv','Sbeox1ML/L','Sbeox1ML/L_sdv','OxsolML/L','OxsolML/L_sdv','Sbeox0PS',
                'Sbeox0PS_sdv','Sbeox1PS','Sbeox1PS_sdv','FlECO-AFL','FlECO-AFL_sdv','Par/lo','Par/lo_sdv','P','P_sdv','WetCDOM','CStarAt0','CStarAt0_sdv','CStarTr','CStarTr_sdv',
                'Analysis_Date_time','Sample','[O2](ml/l)',
                'std_[O2](ml/l)','Rep_1(ml/l)','Rep_2(ml/l)','Filename','Instr','PrimOSens',
                'PrimSOC','SecOSens','SecSOC','WINKLER','WINKLER-DIFF','section']
'''
ordered_list = ['Station-ID','Date','Time','ShTrpStn','Stickr','latD','latM','lonD','lonM','PrDM','PrDM_sdv','T090C','T090C_sdv','T190C','T190C_sdv','C0S/m',
                'C0S/m_sdv','C1S/m','C1S/m_sdv','Sal00','Sal00_sdv','Sal11','Sal11_sdv','Sigma-t00','Sigma-t00_sdv','Sigma-t11','Sigma-t11_sdv','Sbeox0V',
                'Sbeox0V_sdv','Sbeox1V','Sbeox1V_sdv','Sbeox0ML/L','Sbeox0ML/L_sdv','Sbeox1ML/L','Sbeox1ML/L_sdv','OxsolML/L','OxsolML/L_sdv','Sbeox0PS',
                'Sbeox0PS_sdv','Sbeox1PS','Sbeox1PS_sdv','FlECO-AFL','FlECO-AFL_sdv','Par/lo','Par/lo_sdv','P','P_sdv','Analysis_Date_time','Sample','[O2](ml/l)',
                'std_[O2](ml/l)','Rep_1(ml/l)','Rep_2(ml/l)','Rep_3(ml/l)','Rep_4(ml/l)','Rep_5(ml/l)','Rep_6(ml/l)','Filename','Instr','PrimOSens',
                'PrimSOC','SecOSens','SecSOC','WINKLER','WINKLER-DIFF','section']
'''

for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    datasheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in datadict[itm]:
        col = ordered_list.index(itm)
        datasheet.write(row,col,val)
        row += 1

#bottle file
bottledict = botdf.to_dict('list')
bottlesheet = workbook.add_worksheet(shiptrip + '.bot')
first_row=0
#ordered_list = bottledict.keys()
ordered_list = ['Station-ID','Date','Time','ShTrpStn','Stickr','latD','latM','lonD','lonM','PrDM','PrDM_sdv','T090C','T090C_sdv','T190C','T190C_sdv','C0S/m',
                'C0S/m_sdv','C1S/m','C1S/m_sdv','Sal00','Sal00_sdv','Sal11','Sal11_sdv','Sigma-t00','Sigma-t00_sdv','Sigma-t11','Sigma-t11_sdv','Sbeox0V',
                'Sbeox0V_sdv','Sbeox1V','Sbeox1V_sdv','Sbeox0ML/L','Sbeox0ML/L_sdv','Sbeox1ML/L','Sbeox1ML/L_sdv','OxsolML/L','OxsolML/L_sdv','Sbeox0PS',
                'Sbeox0PS_sdv','Sbeox1PS','Sbeox1PS_sdv','FlECO-AFL','FlECO-AFL_sdv','Par/lo','Par/lo_sdv','P','P_sdv','WetCDOM','WetCDOM_sdv','CStarAt0','CStarAt0_sdv','CStarTr','CStarTr_sdv']

float_ordered_list = ['ShTrpStn', 'Stickr', 'latD', 'latM', 'lonD', 'lonM', 'PrDM', 'PrDM_sdv', 'T090C', 'T090C_sdv', 'T190C',
                      'T190C_sdv', 'C0S/m', 'C0S/m_sdv', 'C1S/m', 'C1S/m_sdv', 'Sal00', 'Sal00_sdv', 'Sal11', 'Sal11_sdv', 'Sigma-t00',
                      'Sigma-t00_sdv', 'Sigma-t11', 'Sigma-t11_sdv', 'Sbeox0V', 'Sbeox0V_sdv', 'Sbeox1V', 'Sbeox1V_sdv', 'Sbeox0ML/L',
                      'Sbeox0ML/L_sdv', 'Sbeox1ML/L', 'Sbeox1ML/L_sdv', 'OxsolML/L', 'OxsolML/L_sdv', 'Sbeox0PS', 'Sbeox0PS_sdv',
                      'Sbeox1PS', 'Sbeox1PS_sdv', 'FlECO-AFL', 'FlECO-AFL_sdv', 'Par/lo', 'Par/lo_sdv', 'P', 'P_sdv','WetCDOM','WetCDOM_sdv','CStarAt0','CStarAt0_sdv','CStarTr','CStarTr_sdv']

#This is to accomodate ANOTHER new bot file format :(
bottledict['latM'] = ([s.strip('N') for s in bottledict['latM']])
bottledict['lonM'] = ([s.strip('W') for s in bottledict['latM']])

for key in float_ordered_list:
    for idx, val in enumerate(bottledict[key]):
        bottledict[key][idx] = float(val)

for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    bottlesheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in bottledict[itm]:
        col = ordered_list.index(itm)
        bottlesheet.write(row,col,(val))
        row += 1

#meanO2
o2dict = mo2df.to_dict('list')
o2sheet = workbook.add_worksheet(ship + trip + "_meanO2.txt")
first_row=0
#ordered_list = o2dict.keys()
ordered_list = ['Analysis_Date_time','Sample','[O2](ml/l)','std_[O2](ml/l)','Rep_1(ml/l)','Rep_2(ml/l)']
#ordered_list = ['Analysis_Date_time','Sample','[O2](ml/l)','std_[O2](ml/l)','Rep_1(ml/l)','Rep_2(ml/l)','Rep_3(ml/l)','Rep_4(ml/l)','Rep_5(ml/l)','Rep_6(ml/l)']
float_ordered_list = ['Sample','[O2](ml/l)','std_[O2](ml/l)','Rep_1(ml/l)','Rep_2(ml/l)']

for key in float_ordered_list:
    for idx, val in enumerate(o2dict[key]):
        o2dict[key][idx] = float(val)

for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    o2sheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in o2dict[itm]:
        col = ordered_list.index(itm)
        o2sheet.write(row,col,(val))
        row += 1

#failed titrations
ftdict = failed_titrations.to_dict('list')
failedtitrationssheet = workbook.add_worksheet('failed titrations')
ordered_list = ['Sample','Station-ID','Sbeox0ML/L','WINKLER','WINKLER-DIFF']

float_ordered_list = ['Sample','Sbeox0ML/L','WINKLER','WINKLER-DIFF']
for key in float_ordered_list:
    for idx, val in enumerate(ftdict[key]):
        ftdict[key][idx] = float(val)

for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    failedtitrationssheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in ftdict[itm]:
        col = ordered_list.index(itm)
        failedtitrationssheet.write(row,col,val)
        row += 1

#Instruments
insdict = insdf.to_dict('list')
inssheet = workbook.add_worksheet('instruments')
first_row=0
#ordered_list = insdict.keys()
ordered_list = ['Filename','Instr','PrimOSens','PrimSOC','SecOSens','SecSOC']

insfloat_ordered_list = ['PrimSOC','SecSOC']
for key in insfloat_ordered_list:
    for idx, val in enumerate(insdict[key]):
        insdict[key][idx] = float(val)

for header in ordered_list:
    col=ordered_list.index(header) #keep order.
    inssheet.write(first_row,col,header) #write header
for itm in ordered_list:
    row = first_row+1
    for val in insdict[itm]:
        col = ordered_list.index(itm)
        inssheet.write(row,col,val)
        row += 1


workbook.close()