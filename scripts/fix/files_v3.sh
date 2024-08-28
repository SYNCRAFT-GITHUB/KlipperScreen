#!/bin/bash

random_number=$((RANDOM % 100 + 800))

DIRECTORY_CLONES_PATH="$HOME/fixclones"
PDC_BRANCH="v3"
KS_BRANCH="syncraftx1"

delete_clones_directory() {
    echo "Deleting $DIRECTORY_CLONES_PATH"
    rm -rf $DIRECTORY_CLONES_PATH
}

safe_git_clone() {
    local repo_url="$1"
    local repo_branch="$2"
    local repo_name="$3"

    git clone --quiet -b $repo_branch $repo_url
    if [ $? -eq 0 ]; then
        echo "Sucessfuly cloned $3"
    else
        echo "Unable to clone $3"
        delete_clones_directory
        exit 1
    fi
}

safe_wget() {
    local url="$1"
    local name="$2"

    wget -q $url
    if [ $? -eq 0 ]; then
        echo "Sucessfuly downloaded $2"
    else
        echo "Download failed for $2"
        delete_clones_directory
        exit 1
    fi
}

# Delete directory if found
if [ -d "$DIRECTORY_CLONES_PATH" ]; then
    delete_clones_directory
fi

mkdir "$DIRECTORY_CLONES_PATH"
cd "$DIRECTORY_CLONES_PATH"

safe_git_clone https://github.com/SYNCRAFT-GITHUB/printerdataconfig.git $PDC_BRANCH printerdataconfig
safe_git_clone https://github.com/SYNCRAFT-GITHUB/KlipperScreen.git $KS_BRANCH KlipperScreen
safe_wget https://github.com/SYNCRAFT-GITHUB/mainsail/releases/latest/download/mainsail.zip mainsail


ks_backup_filename="/home/pi/ks-backup-$random_number.conf"

cd "/home/pi/printer_data"

cp config/KlipperScreen.conf $ks_backup_filename

sudo rm -rf config

cp -r "$DIRECTORY_CLONES_PATH/printerdataconfig" config

cd /home/pi

sudo rm -rf printerdataconfig

cp -r "$DIRECTORY_CLONES_PATH/printerdataconfig" .

############################
#   VARIABLE DECLARATION   #
############################

bootconfig='dtparam=audio=on
[pi4]
dtoverlay=vc4-fkms-v3d
max_framebuffers=2
[all]
start_x=1
gpu_mem=128
disable_splash=1
avoid_warnings=1
'

rclocal='#!/bin/sh -e

dmesg --console-off

path="/home/pi/printer_data/config/.bootvideo/bootvideo_intro.mp4"
if [ -e "$path" ]; then
    omxplayer $path &
else
    echo "[SYNCRAFT] Boot Video File not Found."
fi

path="/home/pi/printer_data/gcodes/USB"
if [ -d "$path" ]; then
    echo "[SYNCRAFT] USB Directory OK."
else
    echo "[SYNCRAFT] USB Directory not Found, creating it..."
    cd $path
    mkdir USB
    cd ~
fi

sleep 1 && systemctl daemon-reload && service systemd-udevd --full-restart &

path="/home/pi/printer_data/config/scripts/startup_script.sh"
if [ -e "$path" ]; then
    bash $path
else
    echo "[SYNCRAFT] Startup Script not found."
fi

path="/home/pi/printerdataconfig/scripts/transfer.py"
if [ -e "$path" ]; then
    python3 $path
else
    echo "[SYNCRAFT] transfer.py Script not Found."
fi

path="/home/pi/printerdataconfig/scripts/python/addsaveconfig.py"
if [ -e "$path" ]; then
    python3 $path
else
    echo "[SYNCRAFT] addsaveconfig.py Script not Found."
fi

exit 0
'

usbmountconf='ENABLE=1
MOUNTPOINTS="/home/pi/printer_data/gcodes/USB"
FILESYSTEMS="vfat ext2 ext3 ext4 hfsplus"
MOUNTOPTIONS="sync,noexec,nodev,noatime,nodiratime"
FS_MOUNTOPTIONS="-o udi=pi,gid=pi"
VERBOSE=no
'

udevd='[Service]
PrivateMounts=no
'

##########################################################
#       TRANSFORM BACKUP FILES INTO DEFAULT FILES       #
##########################################################

ptrdc_dir="/home/pi/printerdataconfig"
ptrdc_dir_bckp="$ptrdc_dir/backups"

cp $ptrdc_dir_bckp/backup-printer.cfg $ptrdc_dir/printer.cfg
cp $ptrdc_dir_bckp/backup-variables.cfg $ptrdc_dir/variables.cfg
sudo cp $ks_backup_filename $ptrdc_dir/KlipperScreen.conf
chown pi $ptrdc_dir/printer.cfg
chown pi $ptrdc_dir/variables.cfg
chown pi $ptrdc_dir/KlipperScreen.conf

#############################
#       INSTALL STUFF       #
#############################

cd ~

process='Apply Syncraft X1 KlipperScreen'
echo "[HELPER] START: $process."
sudo rm -r KlipperScreen
cp -r "$DIRECTORY_CLONES_PATH/KlipperScreen" .
echo "[HELPER] DONE: $process."

process='Apply Syncraft Mainsail'
echo "[HELPER] START: $process."
sudo rm -r /home/pi/mainsail
mkdir mainsail
cd /home/pi/mainsail
cp -r "$DIRECTORY_CLONES_PATH/mainsail.zip" .
unzip -q mainsail.zip
rm mainsail.zip
echo "[HELPER] DONE: $process."
cd ~

process='Install OmxPlayer'
echo "[HELPER] START: $process."
sudo apt-get install -qqy omxplayer
echo "[HELPER] DONE: $process."

process='Install UsbMount'
echo "[HELPER] START: $process."
sudo apt-get install -qqy usbmount -y
echo "[HELPER] DONE: $process."

process='Install OmxPlayer'
echo "[HELPER] START: $process."
sudo apt-get install -qqy omxplayer
echo "[HELPER] DONE: $process."

######################################
#         APPLY TEXT VARIABLES       #
######################################

process='Modify RC.LOCAL'
echo "[HELPER] START: $process."
echo -e "$rclocal" | sudo tee /etc/rc.local
sudo chmod +x /etc/rc.local
echo "[HELPER] DONE: $process."

process='Modify BOOTCONFIG'
echo "[HELPER] START: $process."
echo -e "$bootconfig" | sudo tee /boot/config.txt
sudo chmod +x /boot/config.txt
echo "[HELPER] DONE: $process."

process='Modify UsbMount Config'
echo "[HELPER] START: $process."
echo -e "$usbmountconf" | sudo tee /etc/usbmount/usbmount.conf
sudo chmod +x /etc/usbmount/usbmount.conf
echo "[HELPER] DONE: $process."

process='Modify Systemd Udevd'
echo "[HELPER] START: $process."
sudo mkdir /etc/systemd/system/systemd-udevd.service.d
sudo touch "/etc/systemd/system/systemd-udevd.service.d/override.conf"
echo -e "$udevd" | sudo tee /etc/systemd/system/systemd-udevd.service.d/override.conf
sudo chmod +x /etc/systemd/system/systemd-udevd.service.d/override.conf
echo "[HELPER] DONE: $process."

###########################################
#         ADJUST PRINTER_DATA STUFF       #
###########################################

process='Create USB Folder'
echo "[HELPER] START: $process."
cd /home/pi/printer_data/gcodes
mkdir USB_PRINTS
mkdir USB
mkdir .JOB
echo "[HELPER] DONE: $process."
cd ~

process='Create Transfer Python Script'
echo "[HELPER] START: $process."
cd /home/pi/printerdataconfig/scripts
sudo cp /home/pi/printerdataconfig/scripts/backup-transfer.py /home/pi/printerdataconfig/scripts/transfer.py
echo "[HELPER] DONE: $process."

process='Use Python First Transfer Script'
echo "[HELPER] START: $process."
sudo python3 /home/pi/printerdataconfig/scripts/first-transfer.py
echo "[HELPER] DONE: $process."
cd ~

process='Use AddSaveConfig Script'
echo "[HELPER] START: $process."
sudo python3 $ptrdc_dir/scripts/python/addsaveconfig.py
echo "[HELPER] DONE: $process."

process='Create Legacy Text file with false value'
echo "[HELPER] START: $process."
cd /home/pi/printerdataconfig
echo "false" > legacy.txt
sudo chmod 777 /home/pi/printerdataconfig/legacy.txt
echo "[HELPER] DONE: $process."

process='Ensures user permissions for essential folders'
echo "[HELPER] START: $process."

gcodes_dir="/home/pi/printer_data/gcodes"
index_dir="$gcodes_dir/.JOB"
if [ -d "$index_dir" ]; then
    sudo chown -R pi:1000 "$index_dir"
    echo "[HELPER] Permissions updated for $index_dir."
fi
index_dir="$gcodes_dir/USB_PRINTS"
if [ -d "$index_dir" ]; then
    sudo chown -R pi:1000 "$index_dir"
    echo "[HELPER] Permissions updated for $index_dir."
fi
index_dir="$gcodes_dir/USB"
if [ -d "$index_dir" ]; then
    sudo chown -R pi:1000 "$index_dir"
    echo "[HELPER] Permissions updated for $index_dir."
fi

echo "[HELPER] DONE: $process."

echo -e "\n\n[HELPER] DONE."

delete_clones_directory

sudo reboot
