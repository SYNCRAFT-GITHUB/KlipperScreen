#!/bin/bash

cd ~

process='Install Crowsnest (Legacy/V3)'
echo "[HELPER] START: $process."
if [ -e "~/crowsnest" ]; then
    sudo rm -r ~/crowsnest
fi
git clone -b legacy/v3 https://github.com/mainsail-crew/crowsnest.git
cd ~/crowsnest
sudo make install
echo "[HELPER] DONE: $process."

sudo reboot