source("Code/grep.lines.R")

parse.sid.header <- function(file.name) {
  header <- readLines(input.file.name, n=20)
  
  date <- as.Date((strsplit(grep.lines("UTC_StartTime", header), ' = ')[[1]][2]))
  interval <- as.integer(strsplit(grep.lines("LogInterval", header), ' = ')[[1]][2])
  stations <- strsplit(strsplit(grep.lines("Stations", header),' = ')[[1]][2],',')[[1]]
  
  list(date=date, interval=interval, stations=stations)
}
