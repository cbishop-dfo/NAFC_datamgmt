import sqlite3

__author__ = 'KennedyDylan'


def main():
    def setDirectory():
        # default path for DB.
        database = 'thermo.db'

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
    create_deployment_table = """CREATE TABLE IF NOT EXISTS Deployments(
                            id INTEGER,
                            InstrumentType text,
                            SerialNumber text,
                            SiteName text,
                            SiteCode text,
                            Latitude text,
                            Longitude text,
                            StartDate text,
                            StartTime text,                            
                            EndDate text,
                            EndTime text,
                            DeploymentDepth text,
                            SiteDepth text,
                            SamplingSize text,
                            File text,
                            CreationDate text,
                            PRIMARY KEY (id)
                            );"""

    # Table containing all recorded data
    create_data_table = """CREATE TABLE IF NOT EXISTS Data(
                           d_id INTEGER PRIMARY KEY,
                           deployment_id INTEGER NOT NULL,
                           Temperature text,
                           Time text,
                           Year text,
                           FOREIGN KEY (deployment_id) REFERENCES Deployment(id));"""

    # Table to record various locations
    create_location_table = """CREATE TABLE IF NOT EXISTS Location(
                               loc_id INTEGER PRIMARY KEY,
                               SiteName,
                               SiteCode,
                               Latitude,
                               Longitude,
                               SiteDepth
                               );"""

    # Table to keep record of any changes to the data
    create_log_table = """CREATE TABLE DeploymentLog(
                            lkey INTEGER PRIMARY KEY,
                            id_old INTEGER,
                            deployment_id INTEGER NOT NULL, 
                            InstrumentType_old text,
                            InstrumentType_new text,
                            SerialNumber_old text,
                            SerialNumber_new text,
                            SiteName_old text,
                            SiteName_new text,
                            SiteCode_old text,
                            SiteCode_new text,
                            Latitude_old text,
                            Latitude_new text,
                            Longitude_old text,
                            Longitude_new text,
                            StartDate_old text,
                            StartDate_new text,
                            StartTime_old text,
                            StartTime_new text,                            
                            EndDate_old text,
                            EndDate_new text,
                            EndTime_old text,
                            EndTime_new text,
                            DeploymentDepth_old text,
                            DeploymentDepth_new text,
                            SiteDepth_old text,
                            SiteDepth_new text,
                            SamplingSize_old text,
                            SamplingSize_new text,
                            sqlAction VARCHAR(15),
                            Edited DATE,
                            FOREIGN KEY (deployment_id) REFERENCES Deployment(id)
                            );"""

    create_trigger_update = """CREATE TRIGGER update_log AFTER UPDATE ON Deployments
                            BEGIN

                                INSERT INTO DeploymentLog(
                                    id_old,
                                    deployment_id, 
                                    InstrumentType_old,
                                    InstrumentType_new,
                                    SerialNumber_old,
                                    SerialNumber_new ,
                                    SiteName_old,
                                    SiteName_new,
                                    SiteCode_old,
                                    SiteCode_new,
                                    Latitude_old,
                                    Latitude_new,
                                    Longitude_old,
                                    Longitude_new,
                                    StartDate_old,
                                    StartDate_new,
                                    StartTime_old,
                                    StartTime_new,                            
                                    EndDate_old,
                                    EndDate_new,
                                    EndTime_old,
                                    EndTime_new,
                                    DeploymentDepth_old,
                                    DeploymentDepth_new,
                                    SiteDepth_old,
                                    SiteDepth_new,
                                    SamplingSize_old,
                                    SamplingSize_new,
                                    sqlAction,
                                    Edited)

                                values(
                                    old.id,new.id,
                                    old.InstrumentType,new.InstrumentType,
                                    old.SerialNumber,new.SerialNumber,
                                    old.SiteName,new.SiteName,
                                    old.SiteCode,new.SiteCode,
                                    old.Latitude,new.Latitude,
                                    old.Longitude,new.Longitude,
                                    old.StartDate,new.StartDate,
                                    old.StartTime,new.StartTime,
                                    old.EndDate,new.EndDate,
                                    old.EndTime,new.EndTime,
                                    old.DeploymentDepth,new.DeploymentDepth,
                                    old.SiteDepth,new.SiteDepth,
                                    old.SamplingSize,new.SamplingSize,
                                    'INSERT',
                                    DATETIME('NOW'));
                                    END;
                                    """

    create_trigger_insert = """CREATE TRIGGER insert_log AFTER INSERT ON Deployments
                            BEGIN

                                INSERT INTO DeploymentLog(
                                    deployment_id, 
                                    InstrumentType_new,
                                    SerialNumber_new ,
                                    SiteName_new,
                                    SiteCode_new,
                                    Latitude_new,
                                    Longitude_new,
                                    StartDate_new,
                                    StartTime_new,         
                                    EndDate_new,
                                    EndTime_new,
                                    DeploymentDepth_new,
                                    SiteDepth_new,
                                    SamplingSize_new,
                                    sqlAction,
                                    Edited)

                                values(
                                    new.id,
                                    new.InstrumentType,
                                    new.SerialNumber,
                                    new.SiteName,
                                    new.SiteCode,
                                    new.Latitude,
                                    new.Longitude,
                                    new.StartDate,
                                    new.StartTime,
                                    new.EndDate,
                                    new.EndTime,
                                    new.DeploymentDepth,
                                    new.SiteDepth,
                                    new.SamplingSize,
                                    'INSERT',
                                    DATETIME('NOW'));
                                    END;
                                    """

    create_trigger_delete = """CREATE TRIGGER delete_log AFTER DELETE ON Deployments
                            BEGIN

                                INSERT INTO DeploymentLog(
                                    id_old,
                                    InstrumentType_old,
                                    SerialNumber_old,
                                    SiteName_old,
                                    SiteCode_old,
                                    Latitude_old,
                                    Longitude_old,
                                    StartDate_old,
                                    StartTime_old,                
                                    EndDate_old,
                                    EndTime_old,
                                    DeploymentDepth_old,
                                    SiteDepth_old,
                                    SamplingSize_old,
                                    sqlAction,
                                    Edited)

                                values(
                                    old.id,
                                    old.InstrumentType,
                                    old.SerialNumber,
                                    old.SiteName,
                                    old.SiteCode,
                                    old.Latitude,
                                    old.Longitude,
                                    old.StartDate,
                                    old.StartTime,
                                    old.EndDate,
                                    old.EndTime,
                                    old.DeploymentDepth,
                                    old.SiteDepth,
                                    old.SamplingSize,
                                    'DELETE',
                                    DATETIME('NOW'));
                                    END;
                                    """

    if conn is not None:
        c.execute(create_deployment_table)
        c.execute(create_data_table)
        c.execute(create_location_table)
        c.execute(create_log_table)
        c.execute(create_trigger_update)
        c.execute(create_trigger_insert)
        c.execute(create_trigger_delete)
    else:
        print("Error: Cannot Connect To DB.")


if __name__ == '__main__':
    main()
