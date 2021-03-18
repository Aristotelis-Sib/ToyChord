#!/bin/sh
if [ $2 = "True" ]; then
    python3 ~/mychord/startserver.py -h "192.168.1.1" -p $1 -m true -k ($3) -c $4
else
    python3 ~/mychord/startserver.py -h "192.168.1.1" -p $1 -m false
fi
