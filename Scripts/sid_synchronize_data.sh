#!/bin/bash

if [ -z "$SID_HOME" ];
  SID_HOME="$HOME/Workspaces/SID Processing"
fi
cd $SID_HOME

function usage()
{
    echo "Usage: $1 -h HOST -u USER"
}

args=`getopt h:u: $*`
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
        -u)
            user=$2
            shift; shift;;
       --)
           shift; break;;
    esac
done
if [ "$host" == "" -o "$user" == "" ]; then
    usage $0
    exit 1
fi

rsync -av $user@$host:supersid/data/*.csv "Raw Data/"
if [ "$?" != "0" ]; then
	echo Error synchronizing remote data.
	exit 1
fi
