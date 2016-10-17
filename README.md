# SID Signal Processing

## SID Data Transfer and Processing

![](Images/SID Workflow 1.png)

To process SID data you want to download your data from your data host to your local raw data directory

    $ cd <SID SIGNAL PROCESSING HOME>
    $ Scripts/sid_synchronize.sh -s <SITE> -h <HOST> -u <USER>
 
Create anaytical and baseline data for all raw data files not yet processed

    $ Scripts/sid_process_data.sh
    
## SID Data Extraction and Reporting

![](Images/SID Workflow 2.png)

Carefully inspection of SID plots gives a list of SID signals. Once a month I perform a simple workflow to create a SID report for AAVSO from the SID signal data stored in a Numbers spreadsheet:

1. Export spreadsheet as CSV 
1. Prepare AAVSO report
1. Create AAVSO report

e.g. for August 2016 the command sequence 

    $ cd Solar Activity
    $ ../Scripts/sid_prepare_aavos_report.py -i SID\ Log-Table.csv -m 08 -y 2016 > A143.dat
    $ ../Scripts/sid_create_aavso_report.py A143.dat
    
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
- **Code** R code.
- **Output Data** Directory of plot files. File names are of format "SITE_YEAR-MONTH-DAY.png".
- **Raw Data**  Directory for raw data files, one file per day. File names are of format "SITE_YEAR-MONTH-DAY.csv". Columns are signal strengths of VLF transmitter as defined in header rows.
- **Scripts** Directory for shell scripts.
- **Solar Activity** Exported spreadsheet data.