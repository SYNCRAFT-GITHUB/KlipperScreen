#!/bin/bash

script_dir=$(dirname "$(realpath "$0")")
. "$script_dir/safe_network.sh"

DIRECTORY_CLONES_PATH="$HOME/fixclones"

delete_clones_directory() {
    echo "Deleting $DIRECTORY_CLONES_PATH"
    rm -rf $DIRECTORY_CLONES_PATH
}

# Delete directory if found
if [ -d "$DIRECTORY_CLONES_PATH" ]; then
    delete_clones_directory
fi

mkdir "$DIRECTORY_CLONES_PATH"
cd "$DIRECTORY_CLONES_PATH"

safe_git_clone https://github.com/julianschill/klipper-led_effect.git "" klipper-led_effect

process='Install Klipper LED Effect'
cd ~
echo "[HELPER] START: $process."
if [ -e "~/klipper-led_effect" ]; then
    sudo rm -r klipper-led_effect
fi
cp -r "$DIRECTORY_CLONES_PATH/klipper-led_effect" .
bash ~/klipper-led_effect/install-led_effect.sh
echo "[HELPER] install klipper-led_effect DONE."
echo "[HELPER] DONE: $process."

delete_clones_directory

sudo reboot