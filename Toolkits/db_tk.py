import sqlite3
from sqlite3 import Error

"""
Toolkit containing methods useful for Database operations
"""
###########################################################################################################
def setDirectory(database='CTD.db'):

    print("Would you like to change database?")
    print(" Current path: " + database + "\n [1] Yes / [0] No")
    select = input()
    if int(select) == 1:
        print("Input new path:")
        database = input()
        print("\nNew Path: " + database + "\n")
        return database
    elif int(select) == 0:
        return database
    else:
        print("Please Choose [1] Yes / [0] No ...\n")
        setDirectory()

###########################################################################################################

# Creates connection to database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        print(err)


###########################################################################################################