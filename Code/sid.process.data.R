library(dplyr)
library(ggplot2)
library(scales)
library(tidyr)
library(R.utils)

# Set working directory.
sid.signal.processing.home <- Sys.getenv("SID_SIGNAL_PROCESSING_HOME", ".")
setwd(sid.signal.processing.home)

source("Code/parse.sid.header.R")

# Set flag to TRUE when to plot analytical data.
plot.analytical.data.flag = TRUE

# Set flag to TRUE when to process only one raw data file.
process.one.raw.data.file.only.flag = FALSE

# Default directories for analytical, baseline, and raw data files.
analytical.data.dir <- "Analytical Data/"
baseline.data.dir <- "Baseline Data/"
output.data.dir <- "Output Data/"
raw.data.dir <- "Raw Data/"

# Parse command line arguemnts.
args <- commandArgs(asValue=TRUE)
if ("analytical.data.dir" %in% names(args)) analytical.data.dir <- args[["analytical.data.dir"]]
if ("baseline.data.dir" %in% names(args)) baseline.data.dir <- args[["baseline.data.dir"]]
if ("output.data.dir" %in% names(args)) output.data.dir <- args[["output.data.dir"]]
if ("raw.data.dir" %in% names(args)) raw.data.dir <- args[["raw.data.dir"]]

# Create data directories.
for (d in c(analytical.data.dir, baseline.data.dir, output.data.dir)) {
  if (!dir.exists(d)) dir.create(d)
}

# List of analytical data files.
analytical.data.files <- list.files(analytical.data.dir, '.*\\.csv')

# List of raw data files.
raw.data.files <- list.files(raw.data.dir, '.*\\.csv')

# Delta of analytical and raw data files lists.
files <- setdiff(raw.data.files, analytical.data.files)

# Process each file.
for (file.name in files) {

  # Compose input file name.
  input.file.name <- paste(raw.data.dir, file.name, sep="/")
  if (!file.exists(input.file.name)) next
    
  # Compose analytical data file name.
  analytical.data.file.name <- paste(analytical.data.dir, file.name, sep="/")
  if (file.exists(analytical.data.file.name)) next
    
  # Compose baseline data file name.
  baseline.data.file.name <- paste(baseline.data.dir, file.name, sep="/")

  # Compose plot file name.
  plot.file.name <- paste(output.data.dir, sub("\\.csv", "\\.png", file.name), sep="/")
  
  # Parse raw data fiile header.
  header <- parse.sid.header(input.file.name)
  date <- header$date
  interval <- header$interval
  stations <- sub("^DHO38$", "DHO", header$stations)
  
  # Read raw data from file.
  raw.data <- read.csv(input.file.name, header=FALSE, comment.char="#", col.names=stations, as.is=TRUE, na.string="0.000000000000000")

  # Transform raw data into analytical data.
  analytical.data <- raw.data %>%
    
    # Add time.
    mutate(time=seq(as.POSIXct(sprintf("%s 00:00:00",date), "GMT"), as.POSIXct(sprintf("%s 23:59:55",date), "GMT"), interval)) %>%
  
    # Reorganize data using key (station), and value (signal).
    gather(station, signal, one_of(stations)) %>%
    
    # Average signal over 30 seconds.
    mutate(hour=as.POSIXlt(time)[["hour"]]) %>%
    mutate(minute=as.POSIXlt(time)[["min"]]) %>%
    mutate(second=ifelse(as.POSIXlt(time)[["sec"]] < 30, 15, 45)) %>%
    group_by(station, hour, minute, second) %>%
    summarize(time=mean(time, na.rm=TRUE), signal=median(signal, na.rm=TRUE))  %>%
    
    # Drop helper columns.
    ungroup() %>%
    select(time, station, signal)
    
  # Write analytical data to file.
  write.csv(analytical.data, analytical.data.file.name, row.names=FALSE)

  # Plot analytical data.
  if (plot.analytical.data.flag) {
    
    # Start and end time of plot.
    t0 <- as.POSIXct(round(head(analytical.data$time,1),"hour"))
    t1 <- as.POSIXct(round(tail(analytical.data$time,1),"hour"))
    
    # Create plot.
    p <- ggplot(analytical.data) +
      geom_line(aes(x=time, y=signal, col=station)) +
      labs(x="Time [UT]", y="Signal", title=date) +
      scale_x_datetime(breaks=date_breaks("3 hours"), labels=date_format("%H:%M"), minor_breaks=date_breaks("1 hour")) +
      scale_y_log10() +
      theme_bw() +
      theme(axis.text.y=element_blank(), axis.ticks.y=element_blank()) +
      coord_cartesian(xlim=c(t0, t1))
    
    # Write plot to file.
    png(plot.file.name, 2048, 1536)
    print(p)
    dev.off()
    
    # Plot to display.
    print(p)
  }
  
  # Baseline data.
  baseline.data <- analytical.data %>%
    
    # Filter analytical data points from 6:00 to 18:00 ever 30 minutes.
    mutate(hour=as.POSIXlt(time)[["hour"]]) %>%
    mutate(minute=as.POSIXlt(time)[["min"]]) %>%
    filter(hour %in% seq(6,18) & (minute %in% c(0,30))) %>%
    group_by(station, hour, minute) %>%
    summarize(time=mean(time), signal=mean(signal), weight=1) %>%
    
    # Drop helper columns.
    ungroup() %>%
    select(time, station, signal,weight)
    
  # Write baseline data.
  write.csv(baseline.data, baseline.data.file.name, row.names=FALSE)
  
  # Print feedback.
  print(sprintf("%s processed", file.name))
  
  # Check for processing only one raw data file.
  if (process.one.raw.data.file.only.flag) break
}