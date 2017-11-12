#!/usr/bin/python

import astropy.units as u
import calendar

from astroplan import Observer, download_IERS_A
from astropy.coordinates import EarthLocation
from astropy.time import Time, TimeDelta
from getopt import GetoptError, getopt
from sys import argv, exit

def refresh():
    download_IERS_A()

def usage(program):
    print("Sunrise and sunset during a month:")
    print("%s -E -m MONTH -y YEAR [-n NAME] [-l LONGITUDE] [-b LATITUDE] [-z TIMEZONE] [-a ALTITUDE]\n" % program)

    print("Daytime length during a month:")
    print("%s -D -m MONTH -y YEAR [-n NAME] [-l LONGITUDE] [-b LATITUDE] [-z TIMEZONE] [-a ALTITUDE]\n" % program)

    print("Refresh IERS Bulletin A:")
    print("%s -r\n" % program)

    print("This message:")
    print("%s -h" % program)

if __name__ == "__main__":
    try:
        opts, args = getopt(argv[1:], "EDa:b:hl:m:n:ry:z:", ["event", "daytime", "altitude=", "latitude=", "help", "longitude=", "month=", "name=", "refresh", "year=", "timezone="])
    except GetoptError:
        usage(argv[0])
        exit()

    altitude  = 0
    daytime_flag = False
    event_flag = True
    month = None
    latitude  = 0
    longitude = 0
    name = "N/A"
    timezone = "GMT"
    year = None

    for opt, arg in opts:
        if opt in ('-E', '--event'):
            daytime_flag = False
            event_flag = True
        elif opt in ('-D', '--daytime'):
            event_flag = False
            daytime_flag = True
        elif opt in ('-a', '--altitude'):
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
        elif opt in ('-z', '--timezone'):
            timezone = int(arg)

    if month is None or year is None:
        usage(argv[0])
        exit()

    location = EarthLocation.from_geodetic(lon=longitude*u.deg, lat=latitude*u.deg, height=altitude*u.km)
    site =  Observer(location=location, name=name, timezone=timezone)

    first_day_of_month = 1
    last_day_of_month = calendar.monthrange(year,month)[1]
    t0 = Time("{}-{:02d}-{:02d} 12:00:00".format(year,month,first_day_of_month), scale="utc", format="iso")
    t1 = Time("{}-{:02d}-{:02d} 12:00:00".format(year,month,last_day_of_month), scale="utc", format="iso")
    dt = TimeDelta(24 * 60 * 60, format='sec')

    print "# Name: {}".format(site.name)
    print "# Longitude: {}".format(site.location.lon)
    print "# Latitude: {}".format(site.location.lat)
    print "# Timezone: {}".format(site.timezone)
    print "# Altitude: {}".format(site.location.height)

    if daytime_flag:
        print "date, daytime"
        t = Time(t0, format="iso", out_subfmt="date")
        while t <= t1:
            sun_rise  = site.sun_rise_time(t, "previous", 0*u.deg)
            sun_set = site.sun_set_time(t, "next", 0*u.deg)
            print("{} {}".format(t, (sun_set - sun_rise) * 24))
            t += dt
    elif event_flag:
        print "location, date, event"
        t = t0
        while t <= t1:
            sun_rise  = site.sun_rise_time(t, "previous", 0*u.deg)
            sun_set = site.sun_set_time(t, "next", 0*u.deg)
            print("{.iso}, {}".format(sun_rise, "sunrise"))
            print("{.iso}, {}".format(sun_set, "sunset"))
            t += dt
