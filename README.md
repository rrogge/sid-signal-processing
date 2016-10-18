# SID Signal Processing

## SID Data Transfer and Processing

![](Images/SID Workflow 1.png)

To process SID data for my site (LS22) I first download it from Raspberry Pi data host (sidpi) to my local raw data directory

    $ cd ~/Workspace/sid-signal-processing
    $ Scripts/sid_synchronize.sh -s LS22 -h sidpi -u sid
 
Create anaytical and baseline data for all raw data files not yet processed

    $ Scripts/sid_process_data.sh
    
## SID Data Extraction and Reporting

![](Images/SID Workflow 2.png)

Inspection of SID plots gives me a list of SID signals I store in a spreadsheet. Once a month I perform a simple workflow to create a SID report for AAVSO from the SID signal data stored in this spreadsheet:

1. Export spreadsheet as CSV to **Solar Activity** directory
1. Prepare AAVSO report
1. Create AAVSO report

e.g. for August 2016 the command sequence 

    $ Scripts/sid_prepare_aavso_report.py -i Solar\ Activity/SID\ Log-Table.csv -m 8 -y 2016 > A143.dat
    $ Scripts/sid_create_aavso_report.py A143.dat
    
results in one file per transmitter ready to send to AAVSO.

## Directory Structure
  
- **Analytical Data** Directory for analytical data files process from raw data, one file per day. File names are of format "SITE_YEAR-MONTH-DAY.csv". Columns are
    + **time** Time of measurement (YYYY-MM-DD hh:mm:ss)
    + **station** Letter code of the VLF transmitter.
    + **signal** Signal strength.
- **Baseline Data** Directory for baseline data files process from raw data, one file per day. File names are of format "SITE_YEAR-MONTH-DAY.csv". Columns are
    + **time** Time of measurement (YYYY-MM-DD hh:mm:ss)
    + **station** Letter code of the VLF transmitter.
    + **signal** Signal strength.
    + **weight** 1
- **Legacy Data**  Directory for legacy data files, one file per day and transmitter. File names are of format "SITE_TRANSMITTER_YEAR-MONTH-DAY.csv". 
- **Output Data** Directory of plot files. File names are of format "SITE_YEAR-MONTH-DAY.png".
- **R** Directory for R code.
- **Raw Data**  Directory for raw data files, one file per day. File names are of format "SITE_YEAR-MONTH-DAY.csv". Columns are signal strengths of VLF transmitter as defined in header rows.
- **Scripts** Directory for shell scripts.
- **Solar Activity** Exported spreadsheet data.