#!/bin/bash

process='Install Klipper LED Effect'
cd ~
echo "[HELPER] START: $process."
if [ -e "~/klipper-led_effect" ]; then
    sudo rm -r klipper-led_effect
fi
git clone --quiet https://github.com/julianschill/klipper-led_effect.git
bash ~/klipper-led_effect/install-led_effect.sh
echo "[HELPER] install klipper-led_effect DONE."
echo "[HELPER] DONE: $process."

sudo reboot