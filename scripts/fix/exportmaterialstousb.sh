#!/bin/bash

name="[EXPORT MATERIALS TO USB]"

current_time=$(date +'%Y-%m-%d %H-%M')

folder_name="Syncraft Materials - $current_time"
folder_path="/home/pi/printer_data/gcodes/USB/$folder_name"

if [ ! -d "$folder_path" ]; then
    sudo mkdir -p "$folder_path"
    echo "$name CREATED FOLDER: $folder_path"
fi

custom_materials_json_path="/home/pi/KlipperScreen/ks_includes/custom.json"
usb_save_path="$folder_path/materials.json"

if [ -f "$custom_materials_json_path" ]; then
    sudo cp "$custom_materials_json_path" "$usb_save_path"
    echo "$name OK: $custom_materials_json_path -> $usb_save_path"
else
    echo "$name NOT FOUND: $custom_materials_json_path"
fi