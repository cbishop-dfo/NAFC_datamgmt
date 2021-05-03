# -*- coding: utf-8 -*-
"""
Created on Thu May 21 21:10:38 2020

@author: BISHOPC
"""
from Toolkits import cnv_tk
import numpy as np
import pandas as pd

def loadNAFCcnv(datafile):
    print("Reading: " + datafile)
    # Create the cast object
    cast = cnv_tk.Cast(datafile)
    # read the variables for the datafile into the cast object
    cnv_tk.cnv_meta(cast, datafile)
    # Create dataframe from the cast
    df = cnv_tk.cnv_to_dataframe(cast)
    return df, cast

def DropSurfaceDF(new_df):
    # Column for depth/pressure typically comes after the the scan, placing it in the second column
    depth = new_df.columns.values[1]

    # Drop rows based on the condition: where depth < 2
    new_df = new_df.drop(new_df[(new_df[depth].astype(float) < 2)].index)
    return new_df

def splitCast(new_df, pressure):
    
    idx = np.argmax(pressure)
    down = new_df.iloc[:idx]
    
    up = new_df.iloc[idx:][::-1] # Reverse index to orient it as a CTD cast.
    return down, up
#
#@register_series_method
#@register_dataframe_method
def press_check(inputdf):
    """
    Remove pressure reversals from the index.
    """
    press_df = inputdf.copy()
    
    press = press_df.iloc[:,1].astype(float)

    ref = press[0].astype(float)
    #inversions = np.diff(np.r_[press, press[-1]]) < 0
    pressvec=pd.concat([press, pd.Series([-1])])
    inversions = np.diff(pressvec.astype(float)) < 0
    mask = np.zeros_like(inversions)
    for k, p in enumerate(inversions):
        if p:
            ref = press[k]
            cut = press[k + 1 :] < ref
            mask[k + 1 :][cut] = True
    press_df[mask] = np.NaN
    return press_df

#the following are the upper and lower bounds, should this just be a definition or should it be a funtion to do the actual restrictions itself?
def restrict_values(df,variable_name):
    if variable_name == 'temp' or variable_name=='t090C' or variable_name =='t190C':
        lowerbound=-2
        upperbound=25
    if variable_name == 'pressure' or variable_name=='prDM':
        lowerbound=0
        upperbound=4500
    if variable_name == 'oxy':
        lowerbound=0
        upperbound=130
    if variable_name == 'oxypsat':
        lowerbound=0
        upperbound=130
    if variable_name == 'sal' or variable_name == 'salinity':
        lowerbound=0
        upperbound=40
    if variable_name == 'oxy':
        lowerbound=0
        upperbound=130
    if variable_name == 'ph' or variable_name == 'pH':
        lowerbound=0
        upperbound=14
        
    try:
        print(lowerbound,upperbound)
    except NameError:
        lowerbound = None
        upperbound = None
    
    return upperbound, lowerbound
    
    