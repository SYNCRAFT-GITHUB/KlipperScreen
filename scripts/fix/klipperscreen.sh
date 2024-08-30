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

safe_git_clone https://github.com/SYNCRAFT-GITHUB/KlipperScreen.git syncraftx1 KlipperScreen

cd ~

process='Apply Syncraft X1 KlipperScreen'
echo "[HELPER] START: $process."
sudo rm -r KlipperScreen
cp -r "$DIRECTORY_CLONES_PATH/KlipperScreen" .
echo "[HELPER] DONE: $process."

delete_clones_directory

sudo reboot