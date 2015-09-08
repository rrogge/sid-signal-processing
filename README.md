# SID Processing

To process SID data you want to download your data from your SID monitoring computer to the local raw data directory.

    Scripts/sid_synchronize.sh -h sid -u pi
    
Next create anaytical and baseline data for all raw data files not yet processed.

    Scripts/sid_process_data.sh
    
## Directory Structure

- **Analytical Data** Directory for analytical data files process from raw data, one file per day. 
- **Baseline Data** Directory for baseline data files process from raw data, one file per day. 
- **Code** R code.
- **Raw Data**  Directory for raw data files, one file per day. 
- **Scripts** Directory for shell scripts.