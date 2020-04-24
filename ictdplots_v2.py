#!/usr/bin/env python
#
#This is version one of this program - it was written in a hurry needs a full overwrite!
#currently the reset button doesn't work (it removes the points from the second to last step
#back instead of removing all the edits to the beginning)
#The design needs to be completely redone. 
#The buttons should probably be written out as communal functions
#The edited variables should go into a dictionary instead of being written out as individual variables.
#This is probably also true for the original variables (they can probably stay in the dictionary - ie, 
#create depths but then put is back into the original dictionary)
#
#I really want to add a second non-interactive figure window with the original plots from ctdplots 
#(this would have the header information for the cast and all the channels)
#
#Lot's to do!!
#
#Jen Holden, 2015-05-29

import ntpath
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from pylab import *
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import RectangleSelector
from pylab import rcParams
import re
import glob
import os
import shutil
 
 
#this sets the parameter for whether or not to write out the data
comp=False
cancelflag=False
 
###########################
#add the rectangle selector
###########################
 
def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    global x1, x2, y1, y2
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    close()
 
def toggle_selector(event):
    print (' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print (' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print (' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)
 
########################################################################################
#for towed ctds:
########################################################################################
def plot_tow(nam):   
    ##########################################
    #set up the axes so that I can plot depth, 
    #temperature and salinity on the same plot
    ##########################################
    #this changes the figure size
    rcParams['figure.figsize'] = 22, 10
    fig, ax = plt.subplots()
    # Twin the x-axis twice to make independent y-axes.
    axes = [ax, ax.twinx(), ax.twinx()]
    fig.subplots_adjust(right=0.88) #leave room for the extra y-axis
    fig.subplots_adjust(left=0.18) #leave room for buttons
    # Move the last y-axis spine over to the right 
    axes[-1].spines['right'].set_position(('axes', 1.1))
    # To make the border of the right-most axis visible, turn on the frame.
    # This hides the other plots, however, so turn its fill off.
    axes[-1].set_frame_on(True)
    axes[-1].patch.set_visible(False)
    plt.axhline(y=0,color='0.75') 
    plt.axhline(y=-5,color='0.75')   
 
    ####################
    # Then add the plots
    ####################
    ax.set_xlabel("Scans")
    ax.set_xlim([min(scans)-25,max(scans)+25])
    #depths
    A1,=axes[-1].plot(scans,depths, linestyle='-', color='r', linewidth='1', lw=2)
    A1,=axes[-1].plot(nscans,ndepths, linestyle="None", marker='o', color='k', markersize=2)
    axes[-1].set_ylim([min(depths)-10,max(depths)+10])
    axes[-1].set_ylabel("Depth", color='k')
    axes[-1].tick_params(axis='y', colors='k')
    #temperature
    A2,=axes[0].plot(nscans,ntemp, marker='None', linestyle='-', color='b', linewidth='0.5', visible=True, lw=2)
    axes[0].set_ylim([min(temp)-0.1,max(temp)+0.1])
    axes[0].set_ylabel("Temperature", color='b')
    axes[0].tick_params(axis='y', colors='b')
    #salinity
    A3,=axes[1].plot(nscans,nsal, marker='None', linestyle='-', color='g', linewidth='0.5', visible=True, lw=2)
    axes[1].set_ylim([min(sal)-0.05,max(sal)+0.05])
    axes[1].set_ylabel("Salinity", color='g')
    axes[1].tick_params(axis='y', colors='g')
    ax.set_title(nam+"\nDrag cursor to remove points (black points will be saved)")
     
    ################################
    #draw the rectangle
    ################################
    # drawtype is 'box' or 'line' or 'none'
    current_ax=plt.gca() #ax
    toggle_selector.RS = RectangleSelector(current_ax, line_select_callback, drawtype='box', useblit=True, button=[1,3], minspanx=5, minspany=5, spancoords='pixels')
    plt.connect('key_press_event', toggle_selector)
     
    ####################
    #add the check boxes
    ####################
    rax = plt.axes([0.03, 0.75, 0.1, 0.15])
    plt.title("Choose Plots:")
    #check = CheckButtons(rax, ('depth', 'temp', 'sal'), (True, False, False))
    check = CheckButtons(rax, ('depth', 'temp', 'sal'), (True, True, True))
    def checkboxes(label):
        if label == 'depth': A1.set_visible(not A1.get_visible())
        elif label == 'temp': A2.set_visible(not A2.get_visible())
        elif label == 'sal': A3.set_visible(not A3.get_visible())
        plt.draw()
    check.on_clicked(checkboxes)
     
    ##############################
    #add the done button
    ##############################
    def donebutton(event):
        global comp
        comp = True
        close()
        if len(nscans) < len(scans):
            print ("...Saving reduced data set")
            #Write data to a new file
            if os.path.isfile(files+'.orig') != True:
                #import shutil
                shutil.copy2(files,files+'.orig')
                #import os
                os.remove(files)
            g = open(files,'w')  
            #write the header
            for line in range(0,lineind):
                print >>g, splitstr[line]
            #write the data
            printdict = {'scan':['%5s ',0], 'pres':['%11s ',5],'temp':['%11s ',5], 
             'cond':['%11s ',5], 'sal':['%11s ',6], 'sigt':['%11s ',6], 
             'oxy':['%11s ',6], 'flor':['%11s ',6], 'par':['%11s ',6], 'pH':['%11s ',6], 'trp':['%11s ',6], 'tra':['%11s ',6], 'wet':['%11s ',6] }
            #for line in range(0,len(valdict[varsplit[0]])):
             #   for var in varsplit:
              #      g.write(printdict[var][0] % str(valdict[var][line]).ljust(printdict[var][1],'0'))
               # g.write('\n') 
            for line in range(0,len(nscans)):
                g.write(printdict['scan'][0] % int(nscans[line]))
                if npres != 1:
                    g.write(printdict['pres'][0] % str(npres[line]).ljust(printdict['scan'][1], '0'))
                if ntemp != 1:
                    g.write(printdict['temp'][0] % str(ntemp[line]).ljust(printdict['temp'][1], '0'))
                if ncond != 1:
                    g.write(printdict['cond'][0] % str(ncond[line]).ljust(printdict['cond'][1], '0'))
                if nsal != 1:
                    g.write(printdict['sal'][0] % str(nsal[line]).ljust(printdict['sal'][1], '0'))
                if nsigmat != 1:
                    g.write(printdict['sigt'][0] % str(nsigmat[line]).ljust(printdict['sigt'][1], '0'))
                if noxy != 1:
                    g.write(printdict['oxy'][0] % str(noxy[line]).ljust(printdict['oxy'][1], '0'))
                if nflor != 1:
                    g.write(printdict['flor'][0] % str(nflor[line]).ljust(printdict['flor'][1], '0'))
                if npar != 1:
                    g.write(printdict['par'][0] % str(npar[line]).ljust(printdict['par'][1], '0'))
                if nph != 1:
                    g.write(printdict['pH'][0] % str(nph[line]).ljust(printdict['pH'][1], '0'))
                if ntrp != 1:
                    g.write(printdict['trp'][0] % str(ntrp[line]).ljust(printdict['trp'][1], '0'))
                if ntra != 1:
                    g.write(printdict['tra'][0] % str(ntra[line]).ljust(printdict['tra'][1], '0'))
                if nwet != 1:
                    g.write(printdict['wet'][0] % str(nwet[line]).ljust(printdict['wet'][1], '0'))
                g.write('\n') 
             
            g.close()
             
        else:
            print ("...Moving to next file")
         
    def resetbutton(event):
        #global nscans, ntemp, npres, ncond, nsal, nsigmat, ndepths
        nscans = scans; ntemp = temp; npres = pres; ncond = cond; nsal = sal; nsigmat = sigmat; ndepths = depths; noxy = oxy; npar = par; nph = ph; nflor = flor; ntrp = trp; ntra = tra; nwet = wet;
        #print "inside the button:", len(scans), len(nscans)
        close()
         
    def cancelbutton(event):
        close()
        global comp
        comp = True
        print ("...Exiting")
        global cancelflag
        cancelflag = True
             
    #axreset = plt.axes([0.03, 0.42, 0.08, 0.13])
    #breset = Button(axreset, 'Reset')
    #breset.on_clicked(resetbutton)
    axcancel = plt.axes([0.03, 0.26, 0.08, 0.13])
    bcancel = Button(axcancel, 'Cancel')
    bcancel.on_clicked(cancelbutton)
    axdone = plt.axes([0.03, 0.1, 0.08, 0.13])
    bdone = Button(axdone, 'Done\n (Save Changes)')
    bdone.on_clicked(donebutton)
     
    ####################
    #show the plot
    ####################
    plt.show()
    return [x1,x2,y1,y2]
 
########################################################################################
#for vertical ctds:
########################################################################################
def plot_vert(nam):   
#def plot_tow(scans,depths,sal,temp,nscans,ndepths,nam):
    #this changes the figure size
    rcParams['figure.figsize'] = 10, 12
    global nscans, ntemp, npres, ncond, nsal, nsigmat, ndepths, noxy, nflor, npar, nph, ntra, ntrp, nwet
    ##########################################
    #set up the axes so that I can plot depth, 
    #temperature and salinity on the same plot
    ##########################################
 
    fig, ax = plt.subplots()
    # Twin the y-axis twice to make independent x-axes.
    axes = [ax, ax.twiny(), ax.twiny()]
    fig.subplots_adjust(bottom=0.08) #leave room for the extra y-axis
    fig.subplots_adjust(left=0.3)#18) #leave room for buttons
    # Move the x-axis spine to the bottom 
    axes[1].spines['top'].set_position(('axes', 0))
    # To make the border of the right-most axis visible, turn on the frame.
    # This hides the other plots, however, so turn its fill off.
    axes[1].set_frame_on(True)
    axes[1].patch.set_visible(False)
     
    ####################
    # Then add the plots
    ####################
    ax.set_ylabel("Depth")
    #ax.set_xlim([min(depths)-25,max(depths)+25])
    #ax.set_xlim([-25, max(depths)+25])
    #ax.set_ylim([max(depths)+25,min(depths)-25])
    #sigmat
    A1,=axes[-1].plot(sal,depths, linestyle='-', color='r', linewidth='1', lw=2)
    A1,=axes[-1].plot(nsal,ndepths, linestyle="None", marker='o', color='k', markersize=2)
    axes[-1].set_xlim([min(sal)-1,max(sal)+1])
    axes[-1].set_xlabel("sal", color='k')
    axes[-1].tick_params(axis='x', colors='k')
    #temperature
    A2,=axes[0].plot(temp, depths, marker='None', linestyle='-', color='b', linewidth='0.5', visible=True, lw=2)
    axes[0].set_xlim([min(temp)-5,max(temp)+5])
    axes[0].set_xlabel("Temperature", color='b')
    axes[0].tick_params(axis='x', colors='b')
    #salinity
    A3,=axes[1].plot(sigmat,depths, marker='None', linestyle='-', color='g', linewidth='0.5', visible=True, lw=2)
    axes[1].set_xlim([min(sigmat)-0.5,max(sigmat)+0.5])
    axes[1].set_xlabel("Sigmat", color='g')
    axes[1].tick_params(axis='x', colors='g')
    plt.axhline(y=0,color='0.75')
    plt.axhline(y=-5,color='0.75')
    #ax.set_title(nam+"\nDrag cursor to remove points (black points will be saved)")
    plt.title(nam+"\nDrag cursor to remove points (black points will be saved)", y=1.06)
    ################################
    #draw the rectangle
    ################################
    # drawtype is 'box' or 'line' or 'none'
    current_ax=plt.gca() #ax
    toggle_selector.RS = RectangleSelector(current_ax, line_select_callback, drawtype='box', useblit=True, button=[1,3], minspanx=5, minspany=5, spancoords='pixels')
    plt.connect('key_press_event', toggle_selector)
     
    ####################
    #add the check boxes
    ####################
    rax = plt.axes([0.03, 0.75, 0.16, 0.13])
    plt.title("Choose Plots:")
    #check = CheckButtons(rax, ('depth', 'temp', 'sal'), (True, False, False))
    check = CheckButtons(rax, ('sal', 'temp', 'sigmat'), (True, True, True))
    def checkboxes(label):
        if label == 'sal': A1.set_visible(not A1.get_visible())
        elif label == 'temp': A2.set_visible(not A2.get_visible())
        elif label == 'sigmat': A3.set_visible(not A3.get_visible())
        plt.draw()
    check.on_clicked(checkboxes)
     
    ##############################
    #add the done button
    ##############################
    def donebutton(event):
        global comp
        comp = True
        close()
        if len(nsal) < len(sal):
            print ("...Saving reduced data set")
            #Write data to a new file
            if os.path.isfile(files+'.orig') != True:
                #import shutil
                shutil.copy2(files,files+'.orig')
                #import os
                os.remove(files)
            g = open(files,'w')  
            #write the header
            for line in range(0,lineind):
                print >>g, splitstr[line]
            #write the data
            printdict = {'scan':['%5s ',0], 'pres':['%11s ',5],'temp':['%11s ',5], 
             'cond':['%11s ',5], 'sal':['%11s ',6], 'sigt':['%11s ',6], 
             'oxy':['%11s',6], 'flor':['%11s ',6], 'par':['%11s ',6], 'pH':['%11s ',6], 'trp':['%11s ',6], 'tra':['%11s ',6], 'wet':['%11s ',6] }
            #for line in range(0,len(valdict[varsplit[0]])):
             #   for var in varsplit:
              #      g.write(printdict[var][0] % str(valdict[var][line]).ljust(printdict[var][1],'0'))
               # g.write('\n') 
            for line in range(0,len(nscans)):
                g.write(printdict['scan'][0] % int(nscans[line]))
                if npres != 1:
                    g.write(printdict['pres'][0] % str(npres[line]).ljust(printdict['pres'][1], '0'))
                if ntemp != 1:
                    g.write(printdict['temp'][0] % str(ntemp[line]).ljust(printdict['temp'][1], '0'))
                if ncond != 1:
                    g.write(printdict['cond'][0] % str(ncond[line]).ljust(printdict['cond'][1], '0'))
                if nsal != 1:
                    g.write(printdict['sal'][0] % str(nsal[line]).ljust(printdict['sal'][1], '0'))
                if nsigmat != 1:
                    g.write(printdict['sigt'][0] % str(nsigmat[line]).ljust(printdict['sigt'][1], '0'))
                if noxy != 1:
                    g.write(printdict['oxy'][0] % str(noxy[line]).ljust(printdict['oxy'][1], '0'))
                if nflor != 1:
                    g.write(printdict['flor'][0] % str(nflor[line]).ljust(printdict['flor'][1], '0'))
                if npar != 1:
                    g.write(printdict['par'][0] % str(npar[line]).ljust(printdict['par'][1], '0'))
                if nph != 1:
                    g.write(printdict['pH'][0] % str(nph[line]).ljust(printdict['pH'][1], '0'))
                if ntrp != 1:
                    g.write(printdict['trp'][0] % str(ntrp[line]).ljust(printdict['trp'][1], '0'))
                if ntra != 1:
                    g.write(printdict['tra'][0] % str(ntra[line]).ljust(printdict['tra'][1], '0'))
                if nwet != 1:
                    g.write(printdict['wet'][0] % str(nwet[line]).ljust(printdict['wet'][1], '0'))
                g.write('\n') 
             
            g.close()
        else:
            print ("...Moving to next file")
         
    def resetbutton(event):
        #global nscans, ntemp, npres, ncond, nsal, nsigmat, ndepths
        nscans = scans; ntemp = temp; npres = pres; ncond = cond; nsal = sal; nsigmat = sigmat; ndepths = depths; noxy = oxy; nflor = flor; npar = par; nph = ph; ntra = tra; ntrp = trp; nwet = wet
        #print "inside the button:", len(scans), len(nscans)
        close()
         
    def cancelbutton(event):
        close()
        global comp
        comp = True
        print ("...Exiting")
        global cancelflag
        cancelflag = True
             
    #axreset = plt.axes([0.03, 0.42, 0.16, 0.10])
    #breset = Button(axreset, 'Reset')
    #breset.on_clicked(resetbutton)
    axcancel = plt.axes([0.03, 0.26, 0.16, 0.10])
    bcancel = Button(axcancel, 'Cancel')
    bcancel.on_clicked(cancelbutton)
    axdone = plt.axes([0.03, 0.1, 0.16, 0.10])
    bdone = Button(axdone, 'Done\n (Save Changes)')
    bdone.on_clicked(donebutton)
     
    ####################
    #show the plot
    ####################
    plt.show()
    return [x1,x2,y1,y2]
 
########################################################################################
#for xbts:
########################################################################################
def plot_xbt(nam):   
#def plot_tow(scans,depths,sal,temp,nscans,ndepths,nam):
    #this changes the figure size
    rcParams['figure.figsize'] = 10, 12
    global nscans, ntemp, npres, ndepths
    ##########################################
    #set up the axes so that I can plot depth, 
    #temperature and salinity on the same plot
    ##########################################
     
    fig = figure(1)
    fig.subplots_adjust(left=0.3)#18) #leave room for buttons
        
    ####################
    # Then add the plots
    ####################
    plt.ylabel("Depth")
    plt.ylim([min(depths)-1,max(0,max(depths)+1)])
    #temperature
    plt.plot(temp,depths, linestyle='-', color='r', linewidth='1', lw=2)
    plt.plot(ntemp,ndepths, linestyle="None", marker='o', color='k', markersize=2)
    #plt.plot(temp, depths, marker='*', linestyle='-', color='b', linewidth='0.5', visible=True, lw=2)
     
    plt.xlim([min(temp)-5,max(temp)+5])
    plt.xlabel("Temperature", color='k')
    #plt.tick_params(axis='x', colors='b')
    plt.title(nam+"\nDrag cursor to remove points (black points will be saved)")
    ################################
    #draw the rectangle
    ################################
    # drawtype is 'box' or 'line' or 'none'
    current_ax=plt.gca() #ax
    toggle_selector.RS = RectangleSelector(current_ax, line_select_callback, drawtype='box', useblit=True, button=[1,3], minspanx=5, minspany=5, spancoords='pixels')
    plt.connect('key_press_event', toggle_selector)
     
    ##############################
    #add the done button
    ##############################
    def donebutton(event):
        global comp
        comp = True
        close()
        if len(nscans) < len(scans):
            print ("...Saving reduced data set")
            #Write data to a new file
            if os.path.isfile(files+'.orig') != True:
                #import shutil
                shutil.copy2(files,files+'.orig')
                #import os
                os.remove(files)
            g = open(files,'w')  
            #write the header
            for line in range(0,lineind):
                print >>g, splitstr[line]
            #write the data
            printdict = {'scan':['%5s ',0], 'pres':['%11s ',5],'temp':['%11s ',5], 
             'cond':['%11s ',5], 'sal':['%11s ',6], 'sigt':['%11s ',6], 
             'oxy':['%11s ',6], 'flor':['%11s ',6], 'par':['%11s ',6], 'pH':['%11s ',6], 'trp':['%11s ',6], 'tra':['%11s ',6], 'wet':['%11s ',6],}
            #for line in range(0,len(valdict[varsplit[0]])):
             #   for var in varsplit:
              #      g.write(printdict[var][0] % str(valdict[var][line]).ljust(printdict[var][1],'0'))
               # g.write('\n') 
            for line in range(0,len(nscans)):
                g.write(printdict['scan'][0] % int(nscans[line]))
                if npres != 1:
                    g.write(printdict['pres'][0] % str(npres[line]).ljust(printdict['pres'][1], '0'))
                if ntemp != 1:
                    g.write(printdict['temp'][0] % str(ntemp[line]).ljust(printdict['temp'][1], '0'))
                if ncond != 1:
                    g.write(printdict['cond'][0] % str(ncond[line]).ljust(printdict['cond'][1], '0'))
                if nsal != 1:
                    g.write(printdict['sal'][0] % str(nsal[line]).ljust(printdict['sal'][1], '0'))
                if nsigmat != 1:
                    g.write(printdict['sigt'][0] % str(nsigmat[line]).ljust(printdict['sigt'][1], '0'))
                if noxy != 1:
                    g.write(printdict['oxy'][0] % str(noxy[line]).ljust(printdict['oxy'][1], '0'))
                if nflor != 1:
                    g.write(printdict['flor'][0] % str(nflor[line]).ljust(printdict['flor'][1], '0'))
                if npar != 1:
                    g.write(printdict['par'][0] % str(npar[line]).ljust(printdict['par'][1], '0'))
                if nph != 1:
                    g.write(printdict['pH'][0] % str(nph[line]).ljust(printdict['pH'][1], '0'))
                if ntrp != 1:
                    g.write(printdict['trp'][0] % str(ntrp[line]).ljust(printdict['trp'][1], '0'))
                if ntra != 1:
                    g.write(printdict['tra'][0] % str(ntra[line]).ljust(printdict['tra'][1], '0'))
                if nwet != 1:
                    g.write(printdict['wet'][0] % str(nwet[line]).ljust(printdict['wet'][1], '0'))

                g.write('\n') 
             
            g.close()
 
        else:
            print ("...Moving to next file")
         
    def resetbutton(event):
        #global nscans, ntemp, npres, ncond, nsal, nsigmat, ndepths
        nscans = scans; ntemp = temp; npres = pres; ncond = cond; nsal = sal; nsigmat = sigmat; ndepths = depths; noxy = oxy; npar = par; nph = ph; nflor = flor; ntrp = trp; ntra = tra; nwet = wet
        #print "inside the button:", len(scans), len(nscans)
        close()
         
    def cancelbutton(event):
        close()
        global comp
        comp = True
        print ("...Exiting")
        global cancelflag
        cancelflag = True
             
    #axreset = plt.axes([0.03, 0.42, 0.16, 0.10])
    #breset = Button(axreset, 'Reset')
    #breset.on_clicked(resetbutton)
    axcancel = plt.axes([0.03, 0.26, 0.16, 0.10])
    bcancel = Button(axcancel, 'Cancel')
    bcancel.on_clicked(cancelbutton)
    axdone = plt.axes([0.03, 0.1, 0.16, 0.10])
    bdone = Button(axdone, 'Done\n (Save Changes)')
    bdone.on_clicked(donebutton)
     
    ####################
    #show the plot
    ####################
    plt.show()
    return [x1,x2,y1,y2]
 
########################################################################################
#MAIN PART OF PROGRAM
########################################################################################
 
#os.chdir('C:/oceanography_work/ctdplots/tel134')
for files in sorted(glob.glob('./*.p[0-9][0-9][0-9][0-9]')):
    comp = False
    if cancelflag == True:
        #The cancel button has been pushed.
        break
    elif cancelflag == False:
        #Determine the filename
        pathname = files.split('/')
        filename = pathname[len(pathname)-1]
        file1 = filename.split('.')
        name = file1[0] #this will be just the filename with no extension:
        dname=ntpath.dirname(files) #this will be the pathname with no trailing /
        shortname = name[5:8]
        shiptrip = name[0:5]
     
        #Read in the data
        myfile = open(files)
        str1 = myfile.read()
        splitstr = str1.split('\n')
        hdr = splitstr[1]
        possplit = hdr.split(' ')
        myfile.close()
         
        #find all the data after the header    
        for line in range(0,len(splitstr)):
            if splitstr[line] == '-- DATA --':
                lineind = line + 1
                break
             
        ########################################################
        #define the variables
        ########################################################
        #figure out if a vertical (v) or a tow (t)
        possplit = filter(None,possplit)
        type = possplit[10]
        #if the character isn't in the right place, search the header    
        if not type in ['v', 'V', 't', 'T', 'f', 'F']:
            if 'v' in possplit: type = 'v'
            elif 'V' in possplit: type = 'V'
            elif 't' in possplit: type = 't'
            elif 'T' in possplit: type = 'T'
            elif 'f' in possplit: type = 'f'
            elif 'F' in possplit: type = 'F'
            else: print (file1[0], ': No V, T or F, check the header!')
        #print " "
        print (file1[0], "(", type, ")")  
            
        #Add data to dictionary
        with open(files) as fp:
            indatablock = "false"
            valdict = {}
            cou = 0
            lcou = 0
            for line in fp:
                lcou = lcou+1
                if lcou == 2:
                    hdrsplit = re.split('\s+',line.rstrip().lstrip())
                    valdict["filename"] = hdrsplit[0];
                    valdict["LatDeg"] = hdrsplit[1];
                    valdict["LatMin"] = hdrsplit[2];
                    valdict["LonDeg"] = hdrsplit[3];
                    valdict["LonMin"] = hdrsplit[4];
                    valdict["Date"] = hdrsplit[5];
                    valdict["Time"] = hdrsplit[6];
                    valdict["SounderDepth"] = hdrsplit[7];
                    valdict["Inst"] = hdrsplit[8];
                if indatablock =="true":
                    numsplit = re.split('\s+',line.rstrip().lstrip())
                    for i in range(0, len(varsplit)):
                        if varsplit[i] not in valdict:
                            valdict[varsplit[i]] = [float(numsplit[i])]
                        else:
                            valdict[varsplit[i]].append(float(numsplit[i]))
                if "-- DATA --" in line:
                    indatablock = "true"
                if indatablock == "varnames":
                    varsplit = re.split('\s+',line.rstrip().lstrip())
                if "-- END --" in line:
                    if cou == 0:
                        cou = cou+1
                    elif cou ==1:
                        indatablock = "varnames"  
            #print (varsplit) #list of variables
            #print (varnames)
            #print (valdict)  #dictionary with variables in it
                             
        #define the variables for easier plotting
        global scans, temp, pres, cond, sal, sigmat, depths, flor, oxy, par, ph, trp, tra, wet                                    
        scans = valdict['scan'] if 'scan' in valdict else 1
        pres = valdict['pres'] if 'pres' in valdict else 1
        temp = valdict['temp'] if 'temp' in valdict else 1
        cond = valdict['cond'] if 'cond' in valdict else 1
        sal = valdict['sal'] if 'sal' in valdict else 1
        sigmat = valdict['sigt'] if 'sigt' in valdict else 1
        oxy = valdict['oxy'] if 'oxy' in valdict else 1
        flor = valdict['flor'] if 'flor' in valdict else 1
        par = valdict['par'] if 'par' in valdict else 1
        ph = valdict['pH'] if 'pH' in valdict else 1
        trp = valdict['trp'] if 'trp' in valdict else 1
        tra = valdict['tra'] if 'tra' in valdict else 1
        wet = valdict['wet'] if 'wet' in valdict else 1
        
        depths = -1*np.array(pres)
        nam = str(file1[0])
         
        global nscans, ntemp, npres, ncond, nsal, nsigmat, ndepths, noxy, npar, nph,  nflor, ntrp, ntra, nwet 
        nscans = scans; ntemp = temp; npres = pres; ncond = cond; nsal = sal; nsigmat = sigmat; ndepths = depths; noxy = oxy; npar = par; nph = ph; nflor = flor; ntrp = trp; ntra = tra; nwet = wet;
        x1 = min(scans); x2 = max(scans); y1 = min(depths); y2 = max(depths)
        ########################################################      
        #plot according to the type        
        ######################################################## 
          
        if type in ['t', 'T']:
            while comp == False:
                #print "in the main script:", len(scans), len(nscans)
                x1,x2,y1,y2 = plot_tow(nam)
                #x1,x2,y1,y2 = plot_tow(scans,depths,sal,temp,nscans,ndepths,nam)
                 
                #define the boxes boundaries    
                bot = min(y1, y2); top = max(y1, y2)
                lef = min(x1, x2); rgt = max(x1, x2)
                 
                #define the reduced data set
                if 'scan' in valdict:
                    mscans = nscans
                    nscans = []
                if 'pres' in valdict:
                    mpres = npres
                    npres = []
                    mdepths = ndepths
                    ndepths = []
                if 'temp' in valdict:
                    mtemp = ntemp
                    ntemp = []
                if 'cond' in valdict:
                    mcond = ncond
                    ncond = []
                if 'sal' in valdict:
                    msal = nsal
                    nsal = []
                if 'sigt' in valdict:
                    msigmat = nsigmat
                    nsigmat = []
                if 'oxy' in valdict:
                    moxy = noxy
                    noxy = []
                if 'flor' in valdict:
                    mflor = nflor
                    nflor = []
                if 'par' in valdict:
                    mpar = npar
                    npar = []
                if 'pH' in valdict:
                    mph = nph
                    nph = []
                if 'trp' in valdict:
                    mtrp = ntrp
                    ntrp = []
                if 'tra' in valdict:
                    mtra = ntra
                    ntra = []
                if 'wet' in valdict:
                    mwet = nwet
                    nwet = []    
                    
                    
                #mscans = nscans; mpres = npres; mtemp = ntemp; mcond = ncond; msal = nsal; msigmat = nsigmat; mdepths = ndepths; moxy = noxy; mpar = npar; mflor = nflor
                #nscans = []; ntemp = []; npres = []; ncond = []; nsal = []; nsigmat = []; ndepths = []; noxy = []; npar = []; nflor = []
                for i in range(len(mscans)):
                    if not((mscans[i] > lef and mscans[i] < rgt) and (mdepths[i] > bot and mdepths[i] < top)):   
                        if nscans != 1:
                            nscans.append(mscans[i])
                        if npres != 1:
                            npres.append(mpres[i])
                        if ntemp != 1:
                            ntemp.append(mtemp[i])
                        if ncond != 1:
                            ncond.append(mcond[i])
                        if nsal != 1:
                            nsal.append(msal[i])
                        if nsigmat != 1:
                            nsigmat.append(msigmat[i]) 
                        if npar != 1:
                            npar.append(mpar[i])
                        if nph != 1:
                            nph.append(mph[i])
                        if noxy != 1:
                            noxy.append(moxy[i])
                        if nflor != 1:
                            nflor.append(mflor[i])
                        if ntra != 1:
                            ntra.append(mtra[i])
                        if ntrp != 1:
                            ntrp.append(mtrp[i])
                        if nwet != 1:
                            nwet.append(mwet[i]) 
                ndepths = -1*np.array(npres)    
                
        if type in ['f', 'F']:
            #print "...only plotting XBTs - can't save reduced file yet"
            while comp == False:
                x1,x2,y1,y2 = plot_xbt(nam)
                 
                #define the boxes boundaries    
                bot = min(y1, y2); top = max(y1, y2)
                lef = min(x1, x2); rgt = max(x1, x2)
                 
                #define the reduced data set
                if 'scan' in valdict:
                    mscans = nscans
                    nscans = []
                if 'pres' in valdict:
                    mpres = npres
                    npres = []
                    mdepths = ndepths
                    ndepths = []
                if 'temp' in valdict:
                    mtemp = ntemp
                    ntemp = []
                #mscans = nscans; mpres = npres; mtemp = ntemp; mdepths = ndepths;
                #nscans = []; ntemp = []; npres = []; ndepths = [];
                for i in range(len(mtemp)):
                    if not((mtemp[i] > lef and mtemp[i] < rgt) and (mdepths[i] > bot and mdepths[i] < top)):   
                        if nscans != 1:
                            nscans.append(mscans[i])
                        if npres != 1:
                            npres.append(mpres[i])
                        if ntemp != 1:
                            ntemp.append(mtemp[i])    
                ndepths = -1*np.array(npres)    
             
             
        if type in ['v', 'V']:
            #print "...only plotting vertical CTD - can't save reduced file yet"
            while comp == False:
                #print "in the main script:", len(scans), len(nscans)
                x1,x2,y1,y2 = plot_vert(nam)
                #x1,x2,y1,y2 = plot_tow(scans,depths,sal,temp,nscans,ndepths,nam)
                 
                #define the boxes boundaries    
                bot = min(y1, y2); top = max(y1, y2)
                lef = min(x1, x2); rgt = max(x1, x2)
                 
                #define the reduced data set
                if 'scan' in valdict:
                    mscans = nscans
                    nscans = []
                if 'pres' in valdict:
                    mpres = npres
                    npres = []
                    mdepths = ndepths
                    ndepths = []
                if 'temp' in valdict:
                    mtemp = ntemp
                    ntemp = []
                if 'cond' in valdict:
                    mcond = ncond
                    ncond = []
                if 'sal' in valdict:
                    msal = nsal
                    nsal = []
                if 'sigt' in valdict:
                    msigmat = nsigmat
                    nsigmat = []
                if 'oxy' in valdict:
                    moxy = noxy
                    noxy = []
                if 'flor' in valdict:
                    mflor = nflor
                    nflor = []
                if 'par' in valdict:
                    mpar = npar
                    npar = []
                if 'pH' in valdict:
                    mph = nph
                    nph = []
                if 'trp' in valdict:
                    mtrp = ntrp
                    ntrp = []
                if 'tra' in valdict:
                    mtra = ntra
                    ntra = []
                if 'wet' in valdict:
                    mwet = nwet
                    nwet = []
                #mscans = nscans; mpres = npres; mtemp = ntemp; mcond = ncond; msal = nsal; msigmat = nsigmat; mdepths = ndepths; moxy = noxy; mpar = npar; mflor = nflor
                #nscans = []; ntemp = []; npres = []; ncond = []; nsal = []; nsigmat = []; ndepths = []; noxy = []; nflor = []; npar = []
                for i in range(len(mscans)):
                    if not((msal[i] > lef and msal[i] < rgt) and (mdepths[i] > bot and mdepths[i] < top)):   
                        if nscans != 1:
                            nscans.append(mscans[i])
                        if npres != 1:
                            npres.append(mpres[i])
                        if ntemp != 1:
                            ntemp.append(mtemp[i])
                        if ncond != 1:
                            ncond.append(mcond[i])
                        if nsal != 1:
                            nsal.append(msal[i])
                        if nsigmat != 1:
                            nsigmat.append(msigmat[i]) 
                        if npar != 1:
                            npar.append(mpar[i])
                        if nph != 1:
                            nph.append(mph[i])
                        if noxy != 1:
                            noxy.append(moxy[i])
                        if nflor != 1:
                            nflor.append(mflor[i])
                        if ntra != 1:
                            ntra.append(mtra[i])
                        if ntrp != 1:
                            ntrp.append(mtrp[i])
                        if nwet != 1:
                            nwet.append(mwet[i])  
                ndepths = -1*np.array(npres)    
