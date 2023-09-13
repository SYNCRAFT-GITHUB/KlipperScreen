#!/bin/bash

cd ~

moonraker_dir=~/moonraker
script_dir=~/moonraker/scripts/install-moonraker.sh

process='Re-Install Moonraker'

echo "[HELPER] START: $process."
if [ -d "$moonraker_dir" ]; then
    sudo rm -r $moonraker_dir
fi

git clone --quiet -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/moonraker.git

if [ -e "$script_dir" ]; then
    bash $script_dir
fi

echo "[HELPER] DONE: $process."

sudo reboot