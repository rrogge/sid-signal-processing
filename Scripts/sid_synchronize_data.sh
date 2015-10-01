#!/usr/bin/env bash

if [ -z "$SID_SIGNAL_PROCESSING_HOME" ]; then
  SID_SIGNAL_PROCESSING_HOME=`pwd`
fi
cd "$SID_SIGNAL_PROCESSING_HOME"

RAW_DATA_DIR="$SID_SIGNAL_PROCESSING_HOME/Raw Data/"
REMOTE_DATA_DIR="supersid/data/"

function usage()
{
    echo "Usage: $1 -s SITE -h HOST -u USER [-r RAW-DATA-DIR] [-R REMOTE-DATA-DIR]"
}

args=`getopt h:r:s:u:R: $*`
if [ $? != 0 ]; then
    usage $0
    exit 1
fi

set -- $args
for i; do
    case "$i" in
        -h)
            host=$2
            shift; shift;;
        -r)
            RAW_DATA_DIR=$2
            shift; shift;;
        -s)
            site=$2
            shift; shift;;
        -u)
            user=$2
            shift; shift;;
        -R)
            REMOTE_DATA_DIR=$2
            shift; shift;;
       --)
           shift; break;;
    esac
done
if [ -z "$host" -o -z "$site" -o -z "$user" ]; then
    usage $0
    exit 1
fi

rsync -av $user@$host:"$REMOTE_DATA_DIR"/$site*.csv "$RAW_DATA_DIR"

if [ "$?" != "0" ]; then
	echo Error synchronizing remote data.
	exit 1
fi
