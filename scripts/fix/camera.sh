#!/bin/bash

cd ~

sudo rm -r ~/crowsnest
echo "[FIX_CAMERA] removed crowsnest folder from ~."

git clone -b master https://github.com/mainsail-crew/crowsnest.git
echo "[FIX_CAMERA] new crowsnest folder created from git clone."

cd ~/crowsnest
echo "[FIX_CAMERA] cd ~/crowsnest"

sudo make install
echo "[FIX_CAMERA] installed crowsnest."

echo "[FIX_CAMERA] now the system will reboot."
sudo reboot