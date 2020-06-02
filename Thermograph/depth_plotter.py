import sqlite3
from sqlite3 import Error
import datetime
import matplotlib.pyplot as plt


__author__ = 'KennedyDyl'


class Deployments(object):

    def __init__(self, datafile=None):
        self.datafile = datafile
        self.initialize_vars()

    def initialize_vars(self):
        self.id = "null"
        self.InstrumentType = "null"
        self.SiteName = "null"
        self.SiteCode = "null"
        self.InstrumentNum = "null"
        self.Latitude = "null"
        self.Longitude = "null"
        self.DeploymentDepth = "null"
        self.DeploymentDate = "null"
        self.DeploymentTime = "null"
        self.RecoveredDate = "null"
        self.TimeOfRecovery = "null"
        self.SamplingSize = "null"
        self.DeploymentSiteDepth = "null"
        self.data = []
        self.directory = 'thermo.db'  # DB Location.


###########################################################################################################

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as err:
        print(err)


###########################################################################################################


def append_rpf(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM Data")
    f = open("Appended" + ".txt",
             "w+")
    data = []

    datar = c.fetchall()
    for dat in datar:
        try:
            data.append(dat)

            check = dat[3].split(":")
            cLen = check.__len__()
            if cLen > 3:
                check = check[0] + ":" + check[1] + ":" + check[2]
                _datetime = dat[4] + " " + check.replace(".", ":")
                _temp = float(dat[2])

            else:
                _datetime = dat[4] + " " + dat[3].replace(".", ":")
                _temp = float(dat[2])

            f.write(_datetime + " " + _temp.__str__() + "\n")
        except:

            print()
            input("Enter to continue")
            continue

###########################################################################################################


def write_rpf(conn):
    data = Deployments()
    c = conn.cursor()
    c.execute("SELECT * FROM Deployments")
    rows = c.fetchall()

    for row in rows:
        data.id = row[0]
        data.InstrumentType = row[1]
        data.SiteName = row[3]
        data.SiteCode = row[4]
        data.InstrumentNum = row[2]
        data.Latitude = row[5]
        data.Longitude = row[6]
        data.DeploymentDate = row[7]
        data.DeploymentTime = row[8]
        data.RecoveredDate = row[9]
        data.TimeOfRecovery = row[10]
        data.SamplingSize = row[13]
        data.DeploymentSiteDepth = row[11]
        data.DeploymentDepth = row[12]
        data.datafile = row[14]

        d = conn.cursor()
        rowid = row[0]
        d.execute("select * from Data where deployment_id is '{dv}'".format(dv=rowid))
        datar = d.fetchall()
        for dat in datar:

            data.data.append(dat)

            check = dat[3].split(":")
            cLen = check.__len__()
            if cLen > 3:
                check = check[0] + ":" + check[1] + ":" + check[2]
                _datetime = dat[4] + " " + check.replace(".", ":")
                _temp = float(dat[2])

            else:
                try:
                    _datetime = dat[4] + " " + dat[3].replace(".", ":")
                    _temp = float(dat[2])

                except:
                    print("ERROR!   " + data.datafile)
                    print(dat[2])
                    continue

            xaxis.append(_datetime)
            yaxis.append(_temp)


        clr = 'r'
        """
        if data.DeploymentDepth == 'null':
            clr = 'm' # Magenta
        elif float(data.DeploymentDepth) <= 5:
            clr = '#33FFFB' # Cyan
        elif float(data.DeploymentDepth) <= 10:
            clr = '#3385FF' # Blue
        elif float(data.DeploymentDepth) <= 15:
            clr = '#33FF8E' # Light Green
        elif float(data.DeploymentDepth) <= 20:
            clr = '#52FF33' # Green
        elif float(data.DeploymentDepth) <= 25:
            clr = '#FFEF12' # Yellow
        elif float(data.DeploymentDepth) <= 40:
            clr = '#FFBD33' # light Orange
        elif float(data.DeploymentDepth) <= 50:
            clr = '#FF8833' # Orange
        elif float(data.DeploymentDepth) <= 60:
            clr = '#F14D1F' # Blood Orange
        elif float(data.DeploymentDepth) <= 70:
            clr = '#FF1F1F' # Red
        elif float(data.DeploymentDepth) <= 90:
            clr = '#A30000' # Dark Red
        else:
            clr = '#000000' # Black
            print(data.DeploymentDepth)
        """


        date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() for date in xaxis]
        ax.scatter(date_objects, yaxis, color=clr, s=7, label=data.datafile)
        xaxis.clear()
        yaxis.clear()
        print("plotted deployment: " + data.datafile)


###########################################################################################################


def main():

    def setDirectory():
        # default path
        database = 'thermo.db'

        print("Would you like to change database?")
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
    conn = create_connection(database)
    write_rpf(conn)
    append_rpf(conn)
    conn.close()

###########################################################################################################


def plotall():
    print("plotting")
    print()
    date_objects = [datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() for date in xaxis]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.subplots_adjust(left=0.04, top=0.85, bottom=0.06, right=0.90)

    ax.scatter(date_objects, yaxis, color='r', s=1)

    plt.show()

if __name__ == '__main__':
    xaxis = []
    yaxis = []
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    fig.suptitle('Appended Data')
    plt.xlabel('Datetime')
    plt.ylabel('Temperature')
    plt.subplots_adjust(left=0.04, top=0.85, bottom=0.06, right=0.90)

    main()
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')
    plt.show()
    ax.figure.savefig("Appended.png")