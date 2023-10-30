#!/bin/bash

name="[EXPORT LOGS TO USB]"

current_time=$(date +'%Y-%m-%d %H-%M')

folder_name="Syncraft Logs - $current_time"
folder_path="/home/pi/printer_data/gcodes/USB/$folder_name"

if [ ! -d "$folder_path" ]; then
    sudo mkdir -p "$folder_path"
    echo "$name CREATED FOLDER: $folder_path"
fi

klippy_log_path="/home/pi/printer_data/logs/klippy.log"
moonraker_log_path="/home/pi/printer_data/logs/moonraker.log"
crowsnest_log_path="/home/pi/printer_data/logs/crowsnest.log"
klippy_usb_path="$folder_path/klipper.log"
moonraker_usb_path="$folder_path/moonraker.log"
crowsnest_usb_path="$folder_path/crowsnest.log"

if [ -f "$klippy_log_path" ]; then
    sudo cp "$klippy_log_path" "$klippy_usb_path"
    echo "$name OK: $klippy_log_path -> $klippy_usb_path"
else
    echo "$name NOT FOUND: $klippy_log_path"
fi

if [ -f "$moonraker_log_path" ]; then
    sudo cp "$moonraker_log_path" "$moonraker_usb_path"
    echo "$name OK: $moonraker_log_path -> $moonraker_usb_path"
else
    echo "$name NOT FOUND: $moonraker_log_path"
fi

if [ -f "$crowsnest_log_path" ]; then
    sudo cp "$crowsnest_log_path" "$crowsnest_usb_path"
    echo "$name OK: $crowsnest_log_path -> $crowsnest_usb_path"
else
    echo "$name NOT FOUND: $crowsnest_log_path"
fi