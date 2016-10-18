library(dplyr)
library(ggplot2)
library(scales)
library(tidyr)
library(R.utils)

source("R/grep_lines.R")

parse_sid_header <- function(file.name) {
  header <- readLines(input.file.name, n=20)
  date <- as.Date((strsplit(grep_lines("UTC_StartTime", header), ' = ')[[1]][2]))
  interval <- as.integer(strsplit(grep_lines("SampleRate", header), ' = ')[[1]][2])
  station <- strsplit(strsplit(grep_lines("StationID", header),' = ')[[1]][2],',')[[1]]
  list(date=date, interval=interval, station=station)
}

# Set working directory.
sid.signal.processing.home <- Sys.getenv("SID_SIGNAL_PROCESSING_HOME", ".")
setwd(sid.signal.processing.home)

# Set flag to TRUE when to plot analytical data.
plot.analytical.data.flag = TRUE

# Set flag to TRUE when to process only one legacy data file.
process.one.legacy.data.file.only.flag = FALSE

# Default directories for analytical, baseline, and legacy data files.
analytical.data.dir <- "Analytical Data/"
baseline.data.dir <- "Baseline Data/"
output.data.dir <- "Output Data/"
legacy.data.dir <- "Legacy Data/"

# Parse command line arguemnts.
args <- commandArgs(asValue=TRUE)
if ("analytical.data.dir" %in% names(args)) analytical.data.dir <- args[["analytical.data.dir"]]
if ("baseline.data.dir" %in% names(args)) baseline.data.dir <- args[["baseline.data.dir"]]
if ("output.data.dir" %in% names(args)) output.data.dir <- args[["output.data.dir"]]
if ("legacy.data.dir" %in% names(args)) legacy.data.dir <- args[["legacy.data.dir"]]

# Create data directories.
for (d in c(analytical.data.dir, baseline.data.dir, output.data.dir)) {
  if (!dir.exists(d)) dir.create(d)
}

# List of analytical data files.
analytical.data.files <- list.files(analytical.data.dir, '.*\\.csv')

# List of legacy data files.
legacy.data.files <- list.files(legacy.data.dir, '.*\\.csv')

# Delta of analytical and legacy data files lists.
files <- setdiff(legacy.data.files, analytical.data.files)

# Process each file.
for (file.name in files) {

  # Compose input file name.
  input.file.name <- paste(legacy.data.dir, file.name, sep="/")
  if (!file.exists(input.file.name)) next
    
  # Compose analytical data file name.
  analytical.data.file.name <- paste(analytical.data.dir, file.name, sep="/")
  if (file.exists(analytical.data.file.name)) next
    
  # Compose baseline data file name.
  baseline.data.file.name <- paste(baseline.data.dir, file.name, sep="/")

  # Compose plot file name.
  plot.file.name <- paste(output.data.dir, sub("\\.csv", "\\.png", file.name), sep="/")
  
  # Parse legacy data file header.
  header <- parse_sid_header(input.file.name)
  date <- header$date
  interval <- header$interval
  station <- sub("^DHO38$", "DHO", header$station)
  
  # Read legacy data from file.
  legacy.data <- read.csv(input.file.name, header=FALSE, comment.char="#", sep=",", col.names=c("time","signal"), as.is=TRUE)

  # Transform legacy data into analytical data.
  analytical.data <- legacy.data %>%
    
    # Convert data.
    mutate(time=as.POSIXct(time, "GMT")) %>%
    
    # Average signal over 30 seconds.
    mutate(hour=as.POSIXlt(time)[["hour"]]) %>%
    mutate(minute=as.POSIXlt(time)[["min"]]) %>%
    mutate(second=ifelse(as.POSIXlt(time)[["sec"]] < 30, 15, 45)) %>%
    group_by(hour, minute, second) %>%
    summarize(time=mean(time, na.rm=TRUE), signal=median(signal, na.rm=TRUE))  %>%
    
    # Drop helper columns.
    ungroup() %>%
    
    # Add column.
    mutate(station=station) %>%
    
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
  
  # Check for processing only one legacy data file.
  if (process.one.legacy.data.file.only.flag) break
}