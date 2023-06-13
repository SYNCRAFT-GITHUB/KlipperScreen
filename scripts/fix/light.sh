#!/bin/bash

cd ~

sudo rm -r klipper-led_effect

git clone https://github.com/julianschill/klipper-led_effect.git

bash install-led_effect.sh

sudo reboot