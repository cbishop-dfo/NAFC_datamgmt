import sqlite3

__author__ = 'KennedyDyl'
"""
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

"""

def main():
    def setDirectory():
        # default path for DB.
        database = 'CTD.db'

        print("Would you like to change database location?")
        print(" Current path: " + database + "\n y/n")
        select = input()
        if select.lower() == "y":
            print("Input new path:")
            database = input()
            print("\nNew Path: " + database + "\n")
            return database
        elif select.lower() == "n":
            return database
        else:
            print("Please Choose y or n...\n")
            setDirectory()

    database = setDirectory()
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Table containing all meta data
    create_cast_table = """CREATE TABLE IF NOT EXISTS Casts(
                                id INTEGER,
                                ShipName Text,
                                Ship Text,
                                Trip Text,
                                Station Text,
                                Latitude text,
                                Longitude text,
                                SounderDepth text,
                                Instrument text,
                                InstrumentName text,
                                FishSet text,
                                CastType text,
                                Comment text,
                                NumScans text,
                                SamplingRate text,
                                FileType text,
                                ChannelCount text,
                                DataChannels text,
                                Downcast text,
                                Subsample text,
                                MinDepth text,
                                MaxDepth text,
                                FishingStrata text,
                                Met text,
                                CastDatetime text,
                                File text,
                                Language text,
                                Encoding text,
                                Contact text, 
                                Country text,
                                MaintenanceContact text,
                                OrgName text,
                                DataLimit Integer, 
                                PRIMARY KEY (id)
                                );"""

    # Table containing all recorded data
    create_data_table = """CREATE TABLE IF NOT EXISTS Data(
                               did INTEGER NOT NULL,
                               cid INTEGER NOT NULL,
                               scan INTEGER,
                               pres REAL,
                               depth REAL,
                               temp REAL,
                               cond REAL,
                               sal REAL,
                               sigt REAL,
                               oxy REAL,
                               flor REAL,
                               par REAL,
                               pH REAL,
                               trp REAL,
                               tra REAL,
                               wet REAL,
                               PRIMARY KEY (did),                                                                    
                               FOREIGN KEY (cid) REFERENCES Casts(id));"""

    create_sbe_data_table = """CREATE TABLE IF NOT EXISTS SBE_Data(
                              sid INTEGER NOT NULL,
                              cid INTEGER NOT NULL,
                              Scan real,
                              PrdM	 real,
                              T090C real,
                              T190C real,
                              C0S_m real,
                              C1S_m real,
                              Sbeox0V real,
                              Ph	 real,
                              Ph2 real,
                              Sbeox1V real,
                              Par	 real,
                              Par_sat_log real,
                              Par_log real,
                              flSP real,
                              FlSPuv0 real,
                              Upoly0 real,
                              Sbeox0ML_L	 real,
                              Sbeox1ML_L real,
                              Sal00 real,
                              Sal11 real,
                              Sigma_t00 real,
                              Sigma_t11 real,
                              OxsatML_L real,
                              FlECO_AFL real,
                              Tv290C real,
                              WetCDOM real,
                              CStarAt0 real,
                              CStarTr0 real,
                              PRIMARY KEY (sid),                                                                    
                              FOREIGN KEY (cid) REFERENCES Casts(id));"""

    # Table to keep record of all Header Data
    create_header_table = """CREATE TABLE Header(
                            Hkey INTEGER PRIMARY KEY,
                            cid INTEGER,
                            Line text,
                            FOREIGN KEY (cid) REFERENCES Casts(id)
                            );"""

    # Table to keep record of all Header Data
    create_software_table = """CREATE TABLE Software(
                            skey INTEGER PRIMARY KEY,
                            cid INTEGER,
                            Software_Info text,
                            FOREIGN KEY (cid) REFERENCES Casts(id)
                            );"""

    # Table to keep record of all Header Data
    create_instrumentinfo_table = """CREATE TABLE Instrument(
                            ikey INTEGER PRIMARY KEY,
                            cid INTEGER,
                            Instrument_Info text,
                            FOREIGN KEY (cid) REFERENCES Casts(id)
                            );"""

    # Table to keep record of all Header Data
    create_Meteor_table = """CREATE TABLE Meteor(
                            Mkey INTEGER PRIMARY KEY,
                            cid INTEGER,
                            Cloud text,
                            WinDir text,
                            WinSPD text,
                            wwCode text,
                            BarPres text,
                            TempWet text,
                            TempDry text,
                            WavPeroid text,
                            WavHeight text,
                            SwellDir text,
                            SwellPeroid text,
                            SwellHeight text,
                            IceConc text,
                            IceStage text,
                            IceBerg text,
                            FOREIGN KEY (cid) REFERENCES Casts(id)
                            );"""

    # Table to keep record of any changes to the data
    create_log_table = """CREATE TABLE CastLog(
                                lKey INTEGER PRIMARY KEY,
                                id_old  INTEGER,
                                cast_id INTEGER,
                                Ship_old text,
                                Ship_new text,
                                ShipName_old text,
                                ShipName_new text,
                                Trip_old text,
                                Trip_new text,
                                Station_old text,
                                Station_new text,
                                Latitude_old text,
                                Latitude_new text,
                                Longitude_old text,
                                Longitude_new text,
                                SounderDepth_old text,
                                SounderDepth_new text,
                                Instrument_old text,
                                Instrument_new text,
                                InstrumentName_old text,
                                InstrumentName_new text,
                                FishSet_old text,
                                FishSet_new text,
                                CastType_old text,
                                CastType_new text,
                                Comment_old text,
                                Comment_new text,
                                NumScans_old text,
                                NumScans_new text,
                                SamplingRate_old text,
                                SamplingRate_new text,
                                FileType_old text,
                                FileType_new text,
                                ChannelCount_old text,
                                ChannelCount_new text,
                                DataChannels_old text,
                                DataChannels_new text,
                                Downcast_old text,
                                Downcast_new text,
                                Subsample_old text,
                                Subsample_new text,
                                MinDepth_old text,
                                MinDepth_new text,
                                MaxDepth_old text,
                                MaxDepth_new text,
                                FishingStrata_old text,
                                FishingStrata_new text,
                                Met_old text,
                                Met_new text,
                                CastDatetime_old text,
                                CastDatetime_new text,
                                File_old text,
                                File_new text,
                                Language_old text,
                                Language_new text,
                                Encoding_old text,
                                Encoding_new text,
                                Contact_old text, 
                                Contact_new text, 
                                Country_old text,
                                Country_new text,
                                MaintenanceContact_old text,
                                MaintenanceContact_new text,
                                OrgName_old text,
                                OrgName_new text,
                                sqlAction VARCHAR(15),
                                Edited DATE,
                                FOREIGN KEY (cast_id) REFERENCES Casts(id));"""

    create_trigger_update = """CREATE TRIGGER update_log AFTER UPDATE ON Casts
                            BEGIN

                                INSERT INTO CastLog(


                                id_old,
                                cast_id,
                                Ship_old,
                                Ship_new,
                                ShipName_old,
                                ShipName_new,
                                Trip_old,
                                Trip_new,
                                Station_old,
                                Station_new,
                                Latitude_old,
                                Latitude_new,
                                Longitude_old,
                                Longitude_new,
                                SounderDepth_old,
                                SounderDepth_new,
                                Instrument_old,
                                Instrument_new,
                                InstrumentName_old,
                                InstrumentName_new,
                                FishSet_old,
                                FishSet_new,
                                CastType_old,
                                CastType_new,
                                Comment_old,
                                Comment_new,
                                NumScans_old,
                                NumScans_new,
                                SamplingRate_old,
                                SamplingRate_new,
                                FileType_old,
                                FileType_new,
                                ChannelCount_old,
                                ChannelCount_new,
                                DataChannels_old,
                                DataChannels_new,
                                Downcast_old,
                                Downcast_new,
                                Subsample_old,
                                Subsample_new,
                                MinDepth_old,
                                MinDepth_new,
                                MaxDepth_old,
                                MaxDepth_new,
                                FishingStrata_old,
                                FishingStrata_new,
                                Met_old,
                                Met_new,
                                CastDatetime_old,
                                CastDatetime_new,
                                File_old,
                                File_new,
                                Language_old,
                                Language_new,
                                Encoding_old,
                                Encoding_new,
                                Contact_old, 
                                Contact_new, 
                                Country_old,
                                Country_new,
                                MaintenanceContact_old,
                                MaintenanceContact_new,
                                OrgName_old,
                                OrgName_new,
                                sqlAction,
                                Edited)

                                values(      
                                    old.id,
                                    new.id,
                                    old.Ship,
                                    new.Ship,
                                    old.ShipName,
                                    new.ShipName,
                                    old.Trip,
                                    new.Trip,
                                    old.Station,
                                    new.Station,
                                    old.Latitude,
                                    new.Latitude,
                                    old.Longitude,
                                    new.Longitude,
                                    old.SounderDepth,
                                    new.SounderDepth,
                                    old.Instrument,
                                    new.Instrument,
                                    old.InstrumentName,
                                    new.InstrumentName,
                                    old.FishSet,
                                    new.FishSet,
                                    old.CastType,
                                    new.CastType,
                                    old.Comment,
                                    new.Comment,
                                    old.NumScans,
                                    new.NumScans,
                                    old.SamplingRate,
                                    new.SamplingRate,
                                    old.FileType,
                                    new.FileType,
                                    old.ChannelCount,
                                    new.ChannelCount,
                                    old.DataChannels,
                                    new.DataChannels,
                                    old.Downcast,
                                    new.Downcast,
                                    old.Subsample,
                                    new.Subsample,
                                    old.MinDepth,
                                    new.MinDepth,
                                    old.MaxDepth,
                                    new.MaxDepth,
                                    old.FishingStrata,
                                    new.FishingStrata,
                                    old.Met,
                                    new.Met,
                                    old.CastDatetime,
                                    new.CastDatetime,
                                    old.File,
                                    new.File,
                                    old.Language,
                                    new.Language,
                                    old.Encoding,
                                    new.Encoding,
                                    old.Contact,
                                    new.Contact,
                                    old.Country,
                                    new.Country,
                                    old.MaintenanceContact,
                                    new.MaintenanceContact,
                                    old.OrgName,
                                    new.OrgName,                                    
                                    'UPDATE',
                                    DATETIME('NOW'));
                                    END;
                                    """

    create_trigger_insert = """CREATE TRIGGER insert_log AFTER INSERT ON Casts
                            BEGIN

                                INSERT INTO CastLog(
                                    cast_id,
                                    Ship_new,
                                    ShipName_new,
                                    Trip_new,
                                    Station_new,
                                    Latitude_new,
                                    Longitude_new,
                                    SounderDepth_new,
                                    Instrument_new,
                                    InstrumentName_new,
                                    FishSet_new,
                                    CastType_new,
                                    Comment_new,
                                    NumScans_new,
                                    SamplingRate_new,
                                    FileType_new,
                                    ChannelCount_new,
                                    DataChannels_new,
                                    Downcast_new,
                                    Subsample_new,
                                    MinDepth_new,
                                    MaxDepth_new,
                                    FishingStrata_new,
                                    Met_new,
                                    CastDatetime_new,
                                    File_new,
                                    Language_new,
                                    Encoding_new,
                                    Contact_new ,
                                    Country_new,
                                    MaintenanceContact_new,
                                    OrgName_new,
                                    sqlAction,
                                    Edited)

                                values(

                                    new.id,
                                    new.Ship,
                                    new.ShipName,
                                    new.Trip,
                                    new.Station,
                                    new.Latitude,
                                    new.Longitude,
                                    new.SounderDepth,
                                    new.Instrument,
                                    new.InstrumentName,
                                    new.FishSet,
                                    new.CastType,
                                    new.Comment,
                                    new.NumScans,
                                    new.SamplingRate,
                                    new.FileType,
                                    new.ChannelCount,
                                    new.DataChannels,
                                    new.Downcast,
                                    new.Subsample,
                                    new.MinDepth,
                                    new.MaxDepth,
                                    new.FishingStrata,
                                    new.Met,
                                    new.CastDatetime,
                                    new.File,
                                    new.Language,
                                    new.Encoding,
                                    new.Contact,
                                    new.Country,
                                    new.MaintenanceContact,
                                    new.OrgName,                                   
                                    'INSERT',
                                    DATETIME('NOW'));
                                    END;
                                    """

    create_trigger_delete = """CREATE TRIGGER delete_log AFTER DELETE ON Casts
                            BEGIN

                                INSERT INTO CastLog(

                                    id_old,
                                    Ship_old,
                                    ShipName_old,
                                    Trip_old,
                                    Station_old,
                                    Latitude_old,
                                    Longitude_old,
                                    SounderDepth_old,
                                    Instrument_old,
                                    InstrumentName_old,
                                    FishSet_old,
                                    CastType_old,
                                    Comment_old,
                                    NumScans_old,
                                    SamplingRate_old,
                                    FileType_old,
                                    ChannelCount_old,
                                    DataChannels_old,
                                    Downcast_old,
                                    Subsample_old,
                                    MinDepth_old,
                                    MaxDepth_old,
                                    FishingStrata_old,
                                    Met_old,
                                    CastDatetime_old,
                                    File_old,
                                    Language_old,
                                    Encoding_old,
                                    Contact_old,
                                    Country_old,
                                    MaintenanceContact_old,
                                    OrgName_old,
                                    sqlAction,
                                    Edited)

                                values(
                                    old.id,
                                    old.Ship,
                                    old.ShipName,
                                    old.Trip,
                                    old.Station,
                                    old.Latitude,
                                    old.Longitude,
                                    old.SounderDepth,
                                    old.Instrument,
                                    old.InstrumentName,
                                    old.FishSet,
                                    old.CastType,
                                    old.Comment,
                                    old.NumScans,
                                    old.SamplingRate,
                                    old.FileType,
                                    old.ChannelCount,
                                    old.DataChannels,
                                    old.Downcast,
                                    old.Subsample,
                                    old.MinDepth,
                                    old.MaxDepth,
                                    old.FishingStrata,
                                    old.Met,
                                    old.CastDatetime,
                                    old.File,
                                    old.Language,
                                    old.Encoding,
                                    old.Contact,
                                    old.Country,
                                    old.MaintenanceContact,
                                    old.OrgName,
                                    'DELETE',
                                    DATETIME('NOW'));
                                    END;
                                    """

    if conn is not None:
        c.execute(create_cast_table)
        c.execute(create_sbe_data_table)
        c.execute(create_data_table)
        c.execute(create_header_table)
        c.execute(create_software_table)
        c.execute(create_instrumentinfo_table)
        c.execute(create_Meteor_table)
        c.execute(create_log_table)
        c.execute(create_trigger_update)
        c.execute(create_trigger_insert)
        c.execute(create_trigger_delete)
    else:
        print("Error: Cannot Connect To DB.")


if __name__ == '__main__':
    main()
