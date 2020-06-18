# -*- coding: utf-8 -*-
"""
Created on Thu May 21 20:48:23 2020

@author: BISHOPC
"""
### this is a automatic QA script for CNV ctd files, it seperates out the downcast, removes the top 2m of surface data, then it despikes all the channels and finally it restricts certain variables between a set lower and upper bound


import ctd_processing_defs
import numpy as np

#import dir_tk
import cnv_tk
import CNV_QA_def

datafile='79001100.cnv'

[df,cast] = CNV_QA_def.loadNAFCcnv(datafile) #this loads the file


#set column as index


#pressure= new_df.prDM.astype(float)  # negative for depth down
pressure=df.iloc[:,1]

#new_df = df.set_index('prDM')


[down_df, up_df] = CNV_QA_def.splitCast(df,pressure) #split into down and upcast



new_df=CNV_QA_def.press_check(down_df) #gets rid of pressure reversals
# Adds changes to the userInput Header
QA = "** QA Applied: Drop upcast, Keep downcast only."
cast.userInput.append(QA)

new_df = CNV_QA_def.DropSurfaceDF(new_df) #drop top 2m 
QA = "** QA Applied: 2m of surface removed"
cast.userInput.append(QA)


pressure_down=new_df.iloc[:,1]
temp_down=new_df.iloc[:,3]

df_despike= ctd_processing_defs.despike(new_df) # this gets rid of spikes in the dataframe
QA = "** QA Applied: despiking applied to all channels."
cast.userInput.append(QA)
# now we want to restrict each variable inside the dataframe with specific upper and lower bounds, example: restrict prsesure between 0 and 4500:

column_list=cast.ColumnNames
for i in column_list:
    print(i)

    [upperbound, lowerbound]=CNV_QA_def.restrict_values(df_despike,i) #do we want to get the upper/lower values first, and then process elsewhere? or do it all in one go?
    #print(upperbound,lowerbound)
    unrestricted_var=df_despike[i]
    
    if lowerbound != None:
        unrestricted_var[(unrestricted_var >= upperbound)] = np.nan
        unrestricted_var[(unrestricted_var <= lowerbound)] = np.nan
        #unrestricted_var[(lowerbound <= unrestricted_var) & (unrestricted_var >= upperbound)] = np.nan

        df_despike[i]=unrestricted_var
        QA = "** QA Applied: Variable " + i +" Restricted between " + str(lowerbound) + " and " + str(upperbound)
        cast.userInput.append(QA)


new_df=df_despike
# Write out the cast meta data with the dataframe
#cnv_tk.cnv_write(cast, df, ext=".old")
#cnv_tk.cnv_write_simple(cast, df)

                # # edit/modify dataframe
                # new_df = df
                # new_df = modifyDF(new_df)

                # # TODO: Change ".new" to an empty string "" to overwrite original, using ".new" for debugging purposes.
                # # Write the cast meta data with the new/modified dataframe.
cnv_tk.cnv_write(cast, new_df, ext=".new") 