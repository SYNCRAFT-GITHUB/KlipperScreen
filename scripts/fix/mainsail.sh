#!/bin/bash

cd ~

sudo rm -r ~/mainsail
echo "[FIX_MAINSAIL] removed mainsail folder from ~."

mkdir mainsail
echo "[FIX_MAINSAIL] created mainsail folder."

cd ~/mainsail

wget https://github.com/SYNCRAFT-GITHUB/mainsail/releases/latest/download/mainsail.zip
echo "[FIX_MAINSAIL] downloaded latest mainsail release."

unzip mainsail.zip
echo "[FIX_MAINSAIL] unzip mainsail.zip."

echo "[FIX_MAINSAIL] now, the machine will reboot."
sudo reboot