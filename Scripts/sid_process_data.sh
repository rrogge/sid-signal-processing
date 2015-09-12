#!/bin/bash

if [ -z "SID_HOME" ];
  SID_HOME="$HOME/Workspaces/SID Processing"
fi
cd $SID_HOME

R -f "Code/sid.process.data.R"
if [ "$?" != "0" ]; then
	echo Error processing data.
	exit 1
fi
