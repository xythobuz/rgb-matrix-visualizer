#!/bin/sh

echo "Stopping running script"
ssh rpi-rgb-matrix "sudo systemctl disable --now led"
echo
echo

echo "Syncing code"
rsync -avh -e ssh ./*.py rpi-rgb-matrix:~/rgb-matrix-visualizer
echo
echo

echo "Syncing images"
rsync -avh -e ssh ./images/* rpi-rgb-matrix:~/rgb-matrix-visualizer/images
echo
echo

echo "Syncing fonts"
rsync -avh -e ssh ./fonts/* rpi-rgb-matrix:~/rgb-matrix-visualizer/fonts
echo
echo

echo "Starting script"
ssh rpi-rgb-matrix "sudo systemctl enable --now led"
