#!/bin/bash

random_number=$((RANDOM % 100 + 800))

#################
#   CLONE PDC   #
#################

ks_backup_filename="/home/pi/ks-backup-$random_number.conf"

cd "/home/pi/printer_data"

cp config/KlipperScreen.conf $ks_backup_filename

sudo rm -r config

git clone -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/printerdataconfig.git

mv printerdataconfig config

cd /home/pi

sudo rm -r printerdataconfig

git clone -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/printerdataconfig.git

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
git clone --quiet -b syncraftx1 https://github.com/SYNCRAFT-GITHUB/KlipperScreen.git
echo "[HELPER] DONE: $process."

process='Apply Syncraft Mainsail'
echo "[HELPER] START: $process."
sudo rm -r /home/pi/mainsail
mkdir mainsail
cd /home/pi/mainsail
wget -q https://github.com/SYNCRAFT-GITHUB/mainsail/releases/latest/download/mainsail.zip
unzip -q mainsail.zip
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

echo -e "\n\n[HELPER] DONE."

sudo reboot