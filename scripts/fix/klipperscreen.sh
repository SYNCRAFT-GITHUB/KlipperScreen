#!/bin/bash

cd ~

process='Apply Syncraft X1 KlipperScreen'
echo "[HELPER] START: $process."
sudo rm -r KlipperScreen
git clone --quiet -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/KlipperScreen.git
echo "[HELPER] DONE: $process."

sudo reboot