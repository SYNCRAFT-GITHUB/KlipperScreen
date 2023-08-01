#!/bin/bash

cd "/home/$USER/printer_data"

sudo rm -r gcodes

mkdir gcodes

cd gcodes

sudo ln -s /media/ /home/$USER/printer_data/gcodes/

mv media USB

mkdir .JOB

sudo reboot