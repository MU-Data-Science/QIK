#!/bin/bash

export IP=`ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | grep -v '10.10.1.*' | grep -v '172.17.0.1'`

grep -Rnl "localhost" $QIK_HOME | while read -r line ; do
    if [ "$line" == "`readlink -f $0`" ]; then continue; fi
    echo "Processing $line"
    sed -i "s/localhost/$IP/g" $line
done