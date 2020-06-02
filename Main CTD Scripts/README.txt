***Universal_CTD_Database.py****************************************************************************************************************************************

Creates a Sqlite Database capable of storing P File and SBE Data. SBE and P files both store Meta data inside the 
Casts Table, however SBE file data is stored in the "SBE_Data" table and P file data is stored in the "Data" table 
inside the database, both file types share the same table for Meteorological Data called "Meteor".

Database also keeps a log of all INSERTS, UPDATES, and DELETES for Casts table. Logs can be found in CastLog table.

*Note: If any data is deleted/added from/to their respective data table, user should update the DataLimit field inside the Casts
table for the edited cast. DataLimit is a field used in other scripts to help optimize runtime, DataLimit is the number of lines of stored data for each cast.
(updating not necessary just makes for quicker write times).

-------------------------------------------------------------------------------------
The syntax to ADD A COLUMN in a table in SQLite (using the ALTER TABLE statement) is:

ALTER TABLE table_name
  ADD new_column_name column_definition;


-table_name: The name of the table to modify. (ie: "Data" or "SBE_Data")

-new_column_name: The name of the new column to add to the table.(ie: "T290C")

-column_definition: The datatype and definition of the column (NULL or NOT NULL, etc).

ie: ALTER TABLE SBE_Data ADD Sal_11 Text;
-------------------------------------------------------------------------------------


***Universal_CTD_Reader.py******************************************************************************************************************************************

Reader for P Files and SBE Files.
Script takes the file and converts it into a Cast object and is then stored in the database.
User will be prompted to change database path upon execution, Default is "CTD.db".
Script will try and read all supported formats .p and .sbe and write them to the database

-reader for the P files, writes to CTD.db, in "Data" Table
-reader for SBE files, writes to CTD.db, in "SBE_Data" Table

reader pulls column names from the database when creating the dataframe. So if new columns need to be read, create a new field in the coresponding data table.
for SBE files: "SBE_Data" table in database
for P files: "Data" table in database


***Universal_CTD_Writer.py******************************************************************************************************************************************

Script to read CTD files from a sqlite database and write out the files into "Revised" subfolder.

User will be prompted to change Default database on execution, default is CTD.db.
Once database is chosen user can select output format.
Formats include:

1) SBE format
2) P format
3) RSBE format (Revised SBE)
4) NETCDF format

After format is selected, user can choose to write out all files in the database or write out a single file.
All file will be written to a sub folder called "Revised" located inside the working directory.


**NOTE: For Met data related to the sbe files, the xlsx files need to be in the same directory as the running script.


***CTD_Map***********************************************************************************************************************************************************
 
Script takes all casts from the CTD.db and plots them on a Basemap based on their Latitude and Longitude, and writes 
selected casts to a folder in choosn format.
*******************************************************************************************************************
User can select casts by:
1) Ship
2) Ship and Trip
3) Ship, Trip, Station
4) Year
5) Month
6) Year and Month
7) Area Between Specified Min/Max Latitudes and Longitudes

All selected id's to be written out are printed to the information textbox to the right of the map, user can scroll
to view the id's and copy them if needed.

Multiple selects can be done to query multiple casts.
Once casts are selected user can choose an output format to write out to.
supported outputs include:
1) NETCDF Files
2) RSBE Files
3) SBE Files
4) P Files

A reset button is included to clear all selections and redraw casts on the map.
The matplotlib toolbar is included with the map, user can zoom, pan, save, ect.
*******************************************************************************************************************


