exec(open("C:\QA_paths\set_QA_paths.py").read())
from Toolkits import cnv_tk
from Toolkits import dir_tk
from Toolkits import config_deck
from Toolkits import p_tk
import os
from CTD_AutoQA import ctd_processing_defs
import numpy as np
from CTD_AutoQA import CNV_QA_def
"""
Overall_QA
----------
Script to automate the QA process

-Creates Cast object
-Populates cast variables from datafile
-Creates dataframe from populated Cast object
-Drops columns based on instrument number
-Drops columns not found in pfiles
-split into down and upcast
-gets rid of pressure reversals
-drop top 2m 
-gets rid of spikes in the dataframe
-Writes a cnv file using cast and passed in dataframe
-Creates a binned dataframe using despiked df
-writes out various NC files that contain varied dataframes
"""
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dirName = dir_path

    files = dir_tk.confirmSelection(dirName)
    for f in files:
        # changes Dir back to original
        os.chdir(dirName)
        try:
            datafile = f.name
        except:
            datafile = f

        if datafile.lower().endswith(".cnv"):
            # Creates Cast object
            cast = cnv_tk.Cast(datafile)

            # Populates cast variables from datafile
            cnv_tk.cnv_meta(cast, datafile)

            # Creates dataframe from populated Cast object
            df = cnv_tk.cnv_to_dataframe(cast)

            df = cnv_tk.StandardizedDF(cast, df)

            # Drops columns based on instrument number
            c_df = config_deck.dropColumns(cast, df)

            # Drops columns not found in pfiles
            p_df = p_tk.drop_non_pfile(cast, df)
            
            #insert QA steps here:
            
            #pressure=c_df.iloc[:,1] # is there  a better way to get the pressure column without assuming its column 1?
            pressure= c_df["Pressure"].astype('float')
            
            [down_df, up_df] = CNV_QA_def.splitCast(c_df,pressure) #split into down and upcast
            QA = "** QA Applied: Drop upcast, Keep downcast only."
            cast.userInput.append(QA)

            new_df=CNV_QA_def.press_check(down_df) #gets rid of pressure reversals
            QA = "** QA Applied: Remove pressure reversals from downcast"
            cast.userInput.append(QA)
            
            new_df = CNV_QA_def.DropSurfaceDF(new_df) #drop top 2m 
            QA = "** QA Applied: 2m of surface removed"
            cast.userInput.append(QA)
            
            df_despike= ctd_processing_defs.despike(new_df) # this gets rid of spikes in the dataframe
            QA = "** QA Applied: despiking applied to all channels."
            cast.userInput.append(QA)
            
            # now we want to restrict each variable inside the dataframe with specific upper and lower bounds, example: restrict prsesure between 0 and 4500:

    #         column_list=cast.ColumnNames
    #         for i in column_list:
    #             print(i)

    #             [upperbound, lowerbound]=CNV_QA_def.restrict_values(df_despike,i) #do we want to get the upper/lower values first, and then process elsewhere? or do it all in one go?
    # #print(upperbound,lowerbound)
    #             unrestricted_var=df_despike[i]
    
    #             if lowerbound != None:
    #                 unrestricted_var[(unrestricted_var >= upperbound)] = np.nan
    #                 unrestricted_var[(unrestricted_var <= lowerbound)] = np.nan
    #     #unrestricted_var[(lowerbound <= unrestricted_var) & (unrestricted_var >= upperbound)] = np.nan

    #             df_despike[i]=unrestricted_var
    #             QA = "** QA Applied: Variable " + i +" Restricted between " + str(lowerbound) + " and " + str(upperbound)
    #             cast.userInput.append(QA)


            # Writes a cnv file using cast and passed in dataframe.
            #cnv_tk.cnv_write(cast, c_df, ext=".new")
            cnv_tk.cnv_write(cast, df_despike, ext=".new")
            # Bins the dataframe
            #binnedDF = cnv_tk.BinDF(cast, c_df)
            binnedDF = cnv_tk.BinDF(cast, df_despike)


            # Write out NC files
            cnv_tk.NCWrite(cast, df, cast.ship + cast.trip + cast.station + ".nc")
            cnv_tk.NCWrite(cast, binnedDF,  cast.ship + cast.trip + cast.station + "Binned.nc")
            cnv_tk.NCWrite(cast, c_df,  cast.ship + cast.trip + cast.station + "Dropped.nc")

