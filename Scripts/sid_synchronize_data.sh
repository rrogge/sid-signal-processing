#!/bin/bash

if [ -z "$SID_HOME" ];
  SID_HOME="$HOME/Workspaces/SID Statistics"
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

rsync -av $user@$host:supersid/data/LS* "Raw Data/"
if [ "$?" != "0" ]; then
	echo Error getting remote raw data.
	exit 1
fi

git add "Raw Data/"
git commit -m 'Synchronized data.'
git push
