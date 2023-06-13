#!/bin/bash

cd /home/pi/printer_data

rm -r config

git clone -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/printerdataconfig.git

mv printerdataconfig config

cp /home/pi/printer_data/config/backups/backup-printer.cfg /home/pi/printer_data/config/printer.cfg

cp /home/pi/printer_data/config/backups/backup-variables.cfg /home/pi/printer_data/config/variables.cfg

cp /home/pi/printer_data/config/backups/backup-KlipperScreen.conf /home/pi/printer_data/config/KlipperScreen.conf
chown pi /home/pi/printer_data/config/printer.cfg

chown pi /home/pi/printer_data/config/variables.cfg

chown pi /home/pi/printer_data/config/KlipperScreen.conf

python3 /home/pi/printer_data/config/scripts/python/addsaveconfig.py

reboot