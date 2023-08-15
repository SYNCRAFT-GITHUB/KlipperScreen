#!/bin/bash

cd ~

process='Apply Syncraft Mainsail'
echo "[HELPER] START: $process."
sudo rm -r ~/mainsail
mkdir mainsail
cd ~/mainsail
wget -q https://github.com/SYNCRAFT-GITHUB/mainsail/releases/latest/download/mainsail.zip
unzip -q mainsail.zip
echo "[HELPER] DONE: $process."

sudo reboot