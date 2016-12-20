#!/usr/bin/env bash
# Home Assistant Raspberry Pi Installer Kickstarter
# Copyright (C) 2016 Jonathan Baginski - All Rights Reserved
# Permission to copy and modify is granted under the MIT License
# Last revised 5/15/2016

fab_deploy_type=0

while getopts ":nv" opt; do
	case $opt in
		n)
			fab_deploy_type=0
			;;
		v)
			fab_deploy_type=1
			;;
		\?)
			echo "Invalid option: -$OPTARG" >&2
			;;
	esac
done


## Run pre-install apt package dependency checks ##

me=$(whoami)

echo "-- Run apt-get UPDATE"
sudo apt-get -y update
sudo apt-get install -y git python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev

echo "-- Upgrade pip"
sudo /usr/bin/pip install --upgrade pip

echo "-- Install fabric"
sudo /usr/bin/pip install fabric


## Run fab install ##

echo "-- Run HASS installer [deploy type $fab_deploy_type]"
if [ ! -d $(dirname "$0")/.git ]; then
	echo "-- Git clone HASS installer"
	git clone https://github.com/liviuflore/home-assistant-installer.git
	cd home-assistant-installer
fi

fab deploy -H localhost 2>&1 | tee installation_report.txt

exit
