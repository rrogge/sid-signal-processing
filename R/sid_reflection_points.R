library(geosphere)

# Location of SID monitor LS22.
LS22 <- c(+009.1852, +47.6713)

# Locations of monitored VLF transmitters.
DHO <- c(+007.615000, +53.078900)
GQD <- c(-002.883033, +54.731799)
ICV <- c(+009.731011, +40.923127)

# Reflection points of VLF signal halfway between transmitter and monitor.
midpoints <- list(
  "ls22dho/2" = midPoint(LS22, DHO), 
  "ls22gqd/2" = midPoint(LS22, GQD), 
  "ls22icv/2" = midPoint(LS22, ICV)
)
print(midpoints)
