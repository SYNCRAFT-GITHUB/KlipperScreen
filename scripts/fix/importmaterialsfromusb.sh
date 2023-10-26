#!/bin/bash

name="[IMPORT MATERIALS FROM USB]"

usb_location_on_system="/home/pi/printer_data/gcodes/USB/SYNCRAFT"
custom_materials_ks_json_path="/home/pi/custom.json"
usb_json_path="$usb_location_on_system/materials.json"

if [ ! -d "$usb_location_on_system" ]; then
    echo "$name no SYNCRAFT folder detected"
    exit 0
fi

if [ ! -f "$usb_json_path" ]; then
    echo "$name no SYNCRAFT materials.json file detected"
    exit 0
fi

sudo cp "$usb_json_path" "$custom_materials_ks_json_path"
sudo chmod 777 "$custom_materials_ks_json_path"