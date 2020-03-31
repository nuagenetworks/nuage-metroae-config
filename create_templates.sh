#!/usr/bin/env bash
# Script used to create bare-bones templates using the template_helper.py
# script and the contents of the spec file directory. This is for
# experimental use only.
#
COMMAND_FILE=names.txt
if [ -z $1 ]; then
    echo "Please provide the path to the directory of VSD specs to parse"
    echo "Usage: ./templates.sh spec_path [metroae_config_path]"
else
    export VSD_SPECIFICATIONS_PATH=$1
    for tname in $(grep "entity_name" $1/* | cut -d: -f3 | sed "s/\"//g" | sed "s/\,//g"); do
        if [ "$tname" != "DownloadProgress" ] &&
           [ "$tname" != "ForwardingClass" ] &&
           [ "$tname" != "SysmonUplinkConnection" ] &&
           [ "$tname" != "null" ]; then
            echo "- create-root: $tname" > $COMMAND_FILE;
        fi
        if [ -z $2 ]; then
            ./template_helper.py $COMMAND_FILE > $tname.yml
        else
            $2/template_helper.py $COMMAND_FILE > $tname.yml
        fi
    done
fi

