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

PKG_GIT=$(dpkg-query -W --showformat='${Status}\n' git|grep "install ok installed")
echo "-- Checking for python-pip: $PKG_GIT"
if [ "" == "$PKG_GIT" ]; then
	echo "No git. Setting up git."
	sudo apt-get --force-yes --yes install git
fi

PKG_PYDEV=$(dpkg-query -W --showformat='${Status}\n' python-dev|grep "install ok installed")
echo "-- Checking for python-dev: $PKG_PYDEV"
if [ "" == "$PKG_PYDEV" ]; then
	echo "No python-dev. Setting up python-dev."
	sudo apt-get --force-yes --yes install python-dev
fi

PKG_PYPIP=$(dpkg-query -W --showformat='${Status}\n' python-pip|grep "install ok installed")
echo "-- Checking for python-pip: $PKG_PYPIP"
if [ "" == "$PKG_PYPIP" ]; then
	echo "No python-pip. Setting up python-pip."
	sudo apt-get --force-yes --yes install python-pip
fi

sudo apt-get install -y libffi-dev

echo "-- Upgrade pip"
sudo /usr/bin/pip install --upgrade pip

echo "-- Install fabric"
sudo /usr/bin/pip install fabric


## Run fab install ##

echo "-- Run HASS installer [deploy type $fab_deploy_type]"
git clone https://github.com/liviuflore/home-assistant-installer.git
( cd /home/$me/home-assistant-installer && fab deploy:venv=$fab_deploy_type -H localhost 2>&1 | tee installation_report.txt )
exit
