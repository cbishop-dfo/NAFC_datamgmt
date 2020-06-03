RawData consists of raw untrimmed rpf files created from the database.

ValidSampleSize if the sample size is equal to 1 hour, the file gets written to ValidSampleSize.
If false, file is instead written to InvalidSampleSize.

ValidSizeTrimmed is the trimmed rpf files with a valid sample size.

'Headlands'.db is the database containing raw data for the Headland of the current directory

To append trimmed files, run following scripts in ValidSizeTrimmed folder:
1)	Run createBD.py (creates a database called thermo.db)
2)	Run Ingestor.py (writes all the files in the directory into the thermo database)
3)	Run depth_plotter.py (appends data to one file and generates a plot of the data. *Note: when asked to change database say no, unless user manually renamed database, or is under a different directory.)
