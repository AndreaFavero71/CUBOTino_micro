#!/usr/bin/env bash

#######   Andrea Favero,  02 February 2023  ##################################################
#  This bash script activates the venv, and starts the Cubotino_T.py script after the Pi boots
#  When the python script is terminated (GPIO26), the Pi shuts down (check notes before
#  the last row)
##############################################################################################

source /home/pi/cubotino/src/.virtualenvs/bin/activate
cd /home/pi/cubotino/src
python Cubotino_m.py


# ‘halt -p’ command shuts down the raspberry pi
# un-comment 'halt -p' command ONLY when the script works without errors
# un-comment 'halt -p' command ONLY after making an image of the microSD
halt -p

