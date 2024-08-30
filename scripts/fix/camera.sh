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

safe_git_clone https://github.com/mainsail-crew/crowsnest.git legacy/v3 crowsnest

cd ~

process='Install Crowsnest (Legacy/V3)'
echo "[HELPER] START: $process."
if [ -e "~/crowsnest" ]; then
    sudo rm -r ~/crowsnest
fi
cp -r "$DIRECTORY_CLONES_PATH/crowsnest" .
cd ~/crowsnest
sudo make install
echo "[HELPER] DONE: $process."

delete_clones_directory

sudo reboot