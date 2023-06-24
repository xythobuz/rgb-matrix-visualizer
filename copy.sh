#!/bin/bash

if [ $# -ne 0 ] ; then
cat << EOF | rshell
cp pico.py /pyboard
cp util.py /pyboard
cp $1 /pyboard/main.py
EOF
else
cat << EOF | rshell
cp pico.py /pyboard
cp util.py /pyboard
cp life.py /pyboard
EOF
fi
