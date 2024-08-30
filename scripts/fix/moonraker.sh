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

safe_git_clone https://github.com/SYNCRAFT-GITHUB/moonraker.git "" moonraker

cd ~

moonraker_dir=~/moonraker
script_dir=~/moonraker/scripts/install-moonraker.sh

process='Re-Install Moonraker'

echo "[HELPER] START: $process."
if [ -d "$moonraker_dir" ]; then
    sudo rm -r $moonraker_dir
fi

cp -r "$DIRECTORY_CLONES_PATH/moonraker" .

if [ -e "$script_dir" ]; then
    bash $script_dir
fi

echo "[HELPER] DONE: $process."

delete_clones_directory

sudo reboot