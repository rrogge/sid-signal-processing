#!/bin/bash

if [ -z "$SID_HOME" ]; then
  SID_HOME="$HOME/Workspaces/SID Processing"
fi
cd "$SID_HOME"

function usage()
{
    echo "Usage: $1 -s SITE -h HOST -u USER"
}

args=`getopt h:s:u: $*`
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
        -s)
            site=$2
            shift; shift;;
        -u)
            user=$2
            shift; shift;;
       --)
           shift; break;;
    esac
done
if [ -z "$host" -o -z "$site" -o -z "$user" ]; then
    usage $0
    exit 1
fi

rsync -av $user@$host:supersid/data/$site*.csv "Raw Data/"
if [ "$?" != "0" ]; then
	echo Error synchronizing remote data.
	exit 1
fi
