library(geosphere)

# Location of SID monitor.
LS22 <- c(+009.1852, +47.6713)

# Locations of VLF transmitters.
DHO <- c(+007.615000, +53.078900)
GBZ <- c(-003.278456, +54.911643)
GQD <- c(-002.883033, +54.731799)
ICV <- c(+009.731011, +40.923127)

# Reflection points of VLF signal.
midPoint(LS22, DHO)
midPoint(LS22, GQD)
midPoint(LS22, ICV)
