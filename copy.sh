#!/bin/bash

if [ $# -ne 0 ] ; then
cat << EOF | rshell
cp config.py /pyboard
cp pico.py /pyboard
cp util.py /pyboard
cp manager.py /pyboard
cp net.py /pyboard
cp solid.py /pyboard
cp splash.py /pyboard
cp $1 /pyboard/main.py
EOF
else
cat << EOF | rshell
rm /pyboard/main.py
cp config.py /pyboard
cp pico.py /pyboard
cp util.py /pyboard
cp manager.py /pyboard
cp net.py /pyboard
cp solid.py /pyboard
cp splash.py /pyboard
cp life.py /pyboard
EOF
fi
