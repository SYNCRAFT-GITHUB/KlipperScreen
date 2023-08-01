#!/bin/bash

cd ~

sudo rm -r ~/KlipperScreen
echo "[FIX_KLIPPERSCREEN] removed KlipperScreen folder from ~."

git clone -b syncraftx2 https://github.com/SYNCRAFT-GITHUB/KlipperScreen.git
echo "[FIX_KLIPPERSCREEN] new KlipperScreen folder created from git clone."

echo "[FIX_KLIPPERSCREEN] now the system will reboot."
sudo reboot