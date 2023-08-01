#!/bin/bash

cd "/home/$USER/printer_data"

rm -r config

git clone -b syncraftx2 https://github.com/SYNCRAFT-GITHUB/printerdataconfig.git

mv printerdataconfig config

local_pdc_path="/home/$USER/printer_data/config"

if [ -d "/home/$USER/printer_data/gcodes/USB" ]; then
  echo "USB ok."
else
  cd "/home/$USER/printer_data/gcodes"
  sudo ln -s /media/ /home/$USER/printer_data/gcodes/
  mv media USB
fi

sudo reboot