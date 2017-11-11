Sys.setenv(TZ="GMT")

library(ggplot2)
library(dplyr)
library(tidyr)

# Read in SID data. 
raw <- read.csv("Solar Activity/SID Log-Table.csv", sep=";", skip=1, as.is=T, na.strings="", strip.white=T, col.names=c("date","t0","t0_q","t1","t1_q","t2","t2_q","dt", "definition", "transmitter"))
nrow(raw)

# Select only columns needed.
raw <- raw %>% select(date, t0, t1, t2, definition, transmitter)

# Preprocess data.
data <- with(raw, {
  df <- data.frame(date=as.Date(date,"%Y-%m-%d"))
  df$day <- as.numeric(substr(date,9,10))
  df$month <- as.numeric(substr(date,6,7))
  df$year <- as.numeric(substr(date,1,4))
  df$begin <- as.numeric(strptime(paste(date, t0), "%Y-%m-%d %H:%M"))
  df$peak <- as.numeric(strptime(paste(date, t1), "%Y-%m-%d %H:%M"))
  df$end <- as.numeric(strptime(paste(date, t2), "%Y-%m-%d %H:%M"))
  df$definition <- as.factor(definition)
  df$transmitter <- as.factor(transmitter)
  df
})

# Read SID signal classification from file.
classification <- read.csv("Classification.csv", as.is=T)
classification

# Apply SID signal classification.
data$classification <- with(data, {
  duration <- trunc((end - begin) / 60 + 0.5) # minutes
  code <- rep(NA, length(duration))
  for (i in seq(1,length(code))) {
    code[duration >= classification$t0[i] & duration <= classification$t1[i]] = classification$code[i]
  }
  factor(code, levels=c("1-", "1", "1+", "2", "2+", "3", "3+"))
})

# Preprocessing result.
head(data)

first.of.current.month <- as.Date(cut(Sys.Date(),"month"))

DHO <- data %>% 
  
  filter(transmitter == "DHO 23.4") %>%
  
  # Filter any event before the first of current month (= omit current month)
  filter(date < first.of.current.month) %>%
  
  # Set date as mid of month (to group by month).
  mutate(date=as.Date(paste(year,month,"15",sep="-"),"%Y-%m-%d")) %>%
  
  # Pick only needed columns.
  select(date, classification) %>% 
  
  # Group by date and classification.
  group_by(date, classification) %>%
  
  # Summarize events.
  summarize(n=n())

ggplot(DHO) +
  geom_bar(aes(x=date, y=n, fill=classification), stat="identity") +
  scale_fill_brewer(name="Classification", palette="Spectral", direction=-1) +
  labs(title="SID Activity DHO 23.4 kHz", x="Date", y="Number of Events") +
  theme_bw()