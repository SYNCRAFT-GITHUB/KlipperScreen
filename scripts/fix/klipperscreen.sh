#!/bin/bash

cd ~

process='Apply Syncraft Metal KlipperScreen'
echo "[HELPER] START: $process."
sudo rm -r KlipperScreen
git clone --quiet -b metal https://github.com/SYNCRAFT-GITHUB/KlipperScreen.git
echo "[HELPER] DONE: $process."

sudo reboot