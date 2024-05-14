#!/bin/bash

klipper_dir="/home/pi/klipper"
config_file_origin="/home/pi/KlipperScreen/scripts/fix/klipper-flash.config"
config_file_dest="/home/pi/klipper/.config"

if [ -e "$config_file_dest" ]; then
    rm "$config_file_dest"
    echo "Deleted .config file from klipper directory"
fi

echo "Copying KlipperScreen .config file to klipper directory..."
cp "$config_file_origin" "$config_file_dest"

if [ -e "$config_file_dest" ]; then
    echo "COPY OK!"
else
    echo "The .config file is not in the klipper directory."
    echo "This should not happen, exiting..."
    exit 1
fi

echo "CD to klipper directory"
cd "$klipper_dir"

echo "Klipper process will now stop."
sudo service klipper stop

echo "Compiling with \"make\"."
make

echo "Starting flash process..."
echo "######################################"

output=$(make flash FLASH_DEVICE=/dev/ttyACM0 2>&1)
exit_status=$?

# Print the output of the command
echo "$output"

# Check the exit status
if [ $exit_status -ne 0 ]; then
    echo "ERROR"
    exit 1
else
    echo "OK!"
    sudo reboot
fi