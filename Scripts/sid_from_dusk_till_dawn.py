#!/usr/bin/python

import astropy.units as u
import calendar

from astroplan import download_IERS_A
from astroplan import Observer
from astropy.coordinates import EarthLocation
from astropy.time import Time, TimeDelta
from getopt import getopt, GetoptError
from sys import argv, exit

def refresh():
    download_IERS_A()

def usage(program):
    print("%s [-n NAME] [-l LONGITUDE] [-b LATITUDE] [-m MONTH] [-y YEAR] [-a ALTITUDE]" % program)
    print("\n\nRefresh IEARS Bulletin A:\n%s -r" % program)
    print("\n\nThis message:\n%s -h" % program)

if __name__ == "__main__":
    try:
        opts, args = getopt(argv[1:], "a:b:hl:m:n:ry:", ["altitude=", "latitude=", "help", "longitude=", "month=", "name=", "refresh", "year="])
    except GetoptError:
        usage(argv[0])
        exit()

    altitude  = 200.0
    month = 1
    latitude  = 0
    longitude = 0
    name = "N/A"
    year = 1970

    for opt, arg in opts:
        if opt in ('-a', '--altitude'):
            altitude = float(arg)
        elif opt in ('-b', '--latitude'):
            latitude = float(arg)
        elif opt in ('-h', '--help'):
            usage(argv[0])
            exit()
        elif opt in ('-l', '--longitude'):
            longitude = float(arg)
        elif opt in ('-n', '--name'):
            name = arg
        elif opt in ('-m', '--month'):
            month = int(arg)
        elif opt in ('-r', '--refresh'):
            refresh()
            exit()
        elif opt in ('-y', '--year'):
            year = int(arg)

    location = EarthLocation.from_geodetic(longitude*u.deg, latitude*u.deg, altitude*u.km)
    site =  Observer(location=location, name=name, timezone="GMT")

    first_day_of_month = 1
    last_day_of_month = calendar.monthrange(year,month)[1]
    t0 = Time("{}-{:02d}-{:02d} 12:00:00".format(year,month,first_day_of_month), scale="utc")
    t1 = Time("{}-{:02d}-{:02d} 12:00:00".format(year,month,last_day_of_month), scale="utc")
    dt = TimeDelta(24 * 60 * 60, format='sec')

    print "# Name: {}".format(site.name)
    print "# Longitude: {}".format(site.location.longitude)
    print "# Latitude: {}".format(site.location.latitude)
    print "# Altitude: {}".format(site.location.height)
    print "location, date, event"

    t = t0
    while t <= t1:
        sun_rise  = site.sun_rise_time(t, "previous", 0*u.deg)
        print("{0}, {1.iso}, {2}".format(site.name, sun_rise, "sunrise"))
        sun_set = site.sun_set_time(t, "next", 0*u.deg)
        print("{0}, {1.iso}, {2}".format(site.name, sun_set, "sunset"))
        t += dt
