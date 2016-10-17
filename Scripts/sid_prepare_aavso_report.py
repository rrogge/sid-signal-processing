#!/usr/bin/env python

import csv
import getopt
import sys

def main(observer, filename, month, year):

    dates = []
    begin_times = []
    begin_flags = []
    maximum_times = []
    maximum_flags = []
    end_times = []
    end_flags = []
    durations = []
    definitions = []
    transmitters = []

    with open(filename, 'rb') as csvfile:
        try:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            columns = reader.next()
            reader.next() # Skip 2nd line
            for row in reader:
                d=row[0].split("-")
                if d[1] == month and d[0] == year:
                    dates.append(row[0].split("-"))
                    begin_times.append(row[1].split(":"))
                    begin_flags.append(row[2])
                    maximum_times.append(row[3].split(":"))
                    maximum_flags.append(row[4])
                    end_times.append(row[5].split(":"))
                    end_flags.append(row[6])
                    durations.append(row[7])
                    definitions.append(row[8])
                    transmitters.append(row[9])
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    print("OBSERVER %s" % observer)
    print("YEAR %s" % year[2:])
    print("MONTH %s" % month)
    print("")

    for transmitter in set(transmitters):
        print("STATION %s" % transmitter)
        for j in range(len(transmitters)):
            if transmitter == transmitters[j]:
                print("%s %s%s%s %s%s%s %s%s%s %s" % (dates[j][2], begin_times[j][0], begin_times[j][1], begin_flags[j], maximum_times[j][0], maximum_times[j][1], maximum_flags[j], end_times[j][0], end_times[j][1], end_flags[j], definitions[j]))
        print("ENDGROUP")
        print("")

def usage(program):
    print("%s -i FILE -m MONTH -y YEAR [-o OBSERVER]" % program)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:m:o:y:", ["help", "input=", "month=", "observser=", "year="])
    except getopt.GetoptError:
        usage(sys.argv[0])
        sys.exit()

    observer = "A143"
    filename = None
    month = None
    year = None

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(sys.argv[0])
            sys.exit()
        elif opt in ('-i', '--input'):
            filename = arg
        elif opt in ('-m', '--month'):
            month = arg
        elif opt in ('-o', '--observer'):
            observer = arg
        elif opt in ('-y', '--year'):
            year = arg

    if filename==None or month==None or year == None:
        usage(sys.argv[0])
        sys.exit()

    main(observer, filename, month, year)
