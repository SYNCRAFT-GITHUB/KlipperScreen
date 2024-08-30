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

safe_wget https://github.com/SYNCRAFT-GITHUB/mainsail/releases/latest/download/mainsail.zip

cd ~

process='Apply Syncraft Mainsail'
echo "[HELPER] START: $process."
sudo rm -r ~/mainsail
mkdir mainsail
cd ~/mainsail
cp "$DIRECTORY_CLONES_PATH/mainsail.zip" .
unzip -q mainsail.zip
echo "[HELPER] DONE: $process."

delete_clones_directory

sudo reboot