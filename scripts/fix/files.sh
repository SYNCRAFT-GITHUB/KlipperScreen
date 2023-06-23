#!/bin/bash

cd "/home/$USER/printer_data"

rm -r config

git clone -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/printerdataconfig.git

mv printerdataconfig config

local_pdc_path="/home/$USER/printer_data/config"

cp "$local_pdc_path/backups/backup-printer.cfg" "$local_pdc_path/printer.cfg"

cp "$local_pdc_path/backups/backup-variables.cfg" "$local_pdc_path/variables.cfg"

cp "$local_pdc_path/backups/backup-KlipperScreen.conf" "$local_pdc_path/KlipperScreen.conf"

chown "$USER" "$local_pdc_path/printer.cfg"

chown "$USER" "$local_pdc_path/variables.cfg"

chown "$USER" "$local_pdc_path/KlipperScreen.conf"

python3 "$local_pdc_path/scripts/python/addsaveconfig.py"

if [ -d "/home/$USER/printer_data/gcodes/USB" ]; then
  echo "USB ok."
else
  cd "/home/$USER/printer_data/gcodes"
  mkdir "USB"
fi

sudo reboot