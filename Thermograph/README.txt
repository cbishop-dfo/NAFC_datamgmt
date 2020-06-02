--Thermograph Scripts--
________________________________________________________________________________________________________________________________________________________________________________________
CreateDB.py

- Run first to create the thermo database file

________________________________________________________________________________________________________________________________________________________________________________________

Ingestor.py

- Reads all files in the current directory and writes them to the Database file entered. 
***************************************************************
File types that are written to database:
***************************************************************
    1) .dat
    2) .pro
    3) .pipe
    4) .csv
    5) .rpf
    6) .json
    7) Asc files
***************************************************************

________________________________________________________________________________________________________________________________________________________________________________________

checkSample.py

-Reads through .rpf files

 Creates two subfolders in current directory:
  
  [1] - ValidSampleSize 
  [2] - InvalidSampleSize

 script checks if the sample size is equal to 1 hour, if true the file gets written to ValidSampleSize.
 If false, file is instead written to InvalidSampleSize.

________________________________________________________________________________________________________________________________________________________________________________________

plot_trim.py

Script to read in thermograph files(.rpf), trim them and write them back out as well as save trimmed plot.

Script takes all files in the current directory and searches for the .rpf files.
rpf files are read into the Deployment class and opens a trimming plot.

***************************************************************
    List of Instructions/Key Codes For Trimmer:
***************************************************************

    1) Mouse down selects start point for trimming, mouse up selects endpoint. To trim a region hold 
    left click on beginning of bad data and drag to end of bad data then release click. repeat for all bad data in plot.

    2) Enter or space: Confirm selection, trim data from deployment, write to file, save plot as png and close plot.

    3) q: quits trimming and closes plot

    4) r: redraws and updates plot

    5) p: Confirm selection, trim data from deployment, write to file but keeps plot open (mostly used for debugging).

    6) d: Gets standard deviation and trims all points outside of specified deviation (needs improvement).  

***************************************************************
________________________________________________________________________________________________________________________________________________________________________________________

meta_to_csv.py

-reads meta data from Deployments table of the thermo.db file and writes it to a csv file,
csv file name is based on running directory (could add a method to change database path, thermo.db needs to be in running directory.)

________________________________________________________________________________________________________________________________________________________________________________________

depth_plotter.py

- Requires a Database file to run. Reads Data from database and generates a plot of Temperatures vs Datetime. once plot is closed Appended.png will be
saved (Make sure plot is not zoomed in or in a minimized window) and a text file called appended.txt will be generated containing all the Thermograph data from the Data table in one big list.
