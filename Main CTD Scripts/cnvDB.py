import sqlite3

__author__ = 'KennedyDyl'
"""
***cnvDB.py****************************************************************************************************************************************

Creates a Sqlite Database capable of storing CNV Data. Database uses a Standardized Naming scheme in tandem the "cnv_tk.StandardizedDF()"
So when adding data to database besure to convert column names to the Standard.

Database also keeps a log of all INSERTS, UPDATES, and DELETES for Casts table. Logs can be found in CastLog table.

*Note: If any data is deleted/added from/to their respective data table, user should update the DataLimit field inside the Casts
table for the edited cast. DataLimit is a field used in other scripts to help optimize runtime(not necessary, but will improve reading times), DataLimit is the number of lines of stored data for each cast.
(updating not necessary just makes for quicker write times).


Example (Creating a DF to be used in the CNV database):
                cast = cnv_tk.Cast(datafile)
                cnv_tk.cnv_meta(cast, datafile)
                df = cnv_tk.cnv_to_dataframe(cast)
                cast.DataLimit = len(df.index)
                databaseDF = cnv_tk.StandardizedDF(cast, df)
                # Also want to remove spaces from pandas data columns
                databaseDF.columns = databaseDF.columns.str.replace(' ', '')

**CNV.db Database can also be used with the CTD webapp.py to view all meta data. Simply add db file to the same dir as the webapp.

"""

def main():
    def setDirectory():
        # default path for DB.
        database = 'CNV.db'

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
                                Comment text,
                                NumScans text,
                                SamplingRate text,
                                ChannelCount text,
                                DataChannels text,
                                MinDepth text,
                                MaxDepth text,
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
                               scan Integer,
                               Pressure float,
                               Depth  float,
                               Temperature float,
                               SecondaryTemperature float,
                               Conductivity float,
                               SecondaryConductivity float,
                               TransmissometerAttenuation float,
                               TransmissometerTransmission float,
                               Flag float,
                               ChlorophyllAFluorescence float,
                               Fluorescence float,
                               OxygenSaturation float,
                               Irradiance float,
                               PhotosyntheticActiveRadiation float,
                               pH float,
                               Salinity float,
                               SecondarySalinity float,
                               Oxygen float,
                               OxygenRaw float,
                               SecondaryOxygen float,
                               SecondaryOxygenRaw float,
                               Density float,
                               SecondaryDensity float,
                               CDOMFluorescence float,
                               PRIMARY KEY (did),                                                                    
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
                                Comment_old text,
                                Comment_new text,
                                NumScans_old text,
                                NumScans_new text,
                                SamplingRate_old text,
                                SamplingRate_new text,
                                ChannelCount_old text,
                                ChannelCount_new text,
                                DataChannels_old text,
                                DataChannels_new text,
                                MinDepth_old text,
                                MinDepth_new text,
                                MaxDepth_old text,
                                MaxDepth_new text,
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
                                Comment_old,
                                Comment_new,
                                NumScans_old,
                                NumScans_new,
                                SamplingRate_old,
                                SamplingRate_new,
                                ChannelCount_old,
                                ChannelCount_new,
                                DataChannels_old,
                                DataChannels_new,
                                MinDepth_old,
                                MinDepth_new,
                                MaxDepth_old,
                                MaxDepth_new,
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
                                    old.Comment,
                                    new.Comment,
                                    old.NumScans,
                                    new.NumScans,
                                    old.SamplingRate,
                                    new.SamplingRate,
                                    old.ChannelCount,
                                    new.ChannelCount,
                                    old.DataChannels,
                                    new.DataChannels,
                                    old.MinDepth,
                                    new.MinDepth,
                                    old.MaxDepth,
                                    new.MaxDepth,
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
                                    Comment_new,
                                    NumScans_new,
                                    SamplingRate_new,
                                    ChannelCount_new,
                                    DataChannels_new,
                                    MinDepth_new,
                                    MaxDepth_new,
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
                                    new.Comment,
                                    new.NumScans,
                                    new.SamplingRate,
                                    new.ChannelCount,
                                    new.DataChannels,
                                    new.MinDepth,
                                    new.MaxDepth,
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
                                    Comment_old,
                                    NumScans_old,
                                    SamplingRate_old,
                                    ChannelCount_old,
                                    DataChannels_old,
                                    MinDepth_old,
                                    MaxDepth_old,
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
                                    old.Comment,
                                    old.NumScans,
                                    old.SamplingRate,
                                    old.ChannelCount,
                                    old.DataChannels,
                                    old.MinDepth,
                                    old.MaxDepth,
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
        c.execute(create_data_table)
        c.execute(create_header_table)
        c.execute(create_software_table)
        c.execute(create_instrumentinfo_table)
        c.execute(create_log_table)
        c.execute(create_trigger_update)
        c.execute(create_trigger_insert)
        c.execute(create_trigger_delete)
    else:
        print("Error: Cannot Connect To DB.")


if __name__ == '__main__':
    main()
