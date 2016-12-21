#!/usr/bin/env bash
# eg: ./hass_installer.sh -vsc /vagrant/hassconfig -h 192.168.1.21 -u pi

virtualenv=False
usessl=True
config_path=''
target_host=localhost
target_user=$USER

TEMP=`getopt -o vschu: --long virtual,ssl,config:,host:,user: -n 'hass_installer.sh' -- "$@"`
if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 1 ; fi
eval set -- "$TEMP"

while true ; do
    case "$1" in
        -v|--virtual) virtualenv=True ; shift ;;
        -s|--ssl) usessl=True ; shift ;;
        -c|--config) config_path=$2 ; shift 2 ;;
        -h|--host) target_host=$2 ; shift 2 ;;
        -u|--user) target_user=$2 ; shift 2 ;;
        --) shift ; break ;;
        \?) echo "Invalid option: -$OPTARG" >&2 ;;
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

echo "-- Run HASS installer [v:$virtualenv s:$usessl c:$config_path]"
if [ ! -d $(dirname "$0")/.git ]; then
    echo "-- Git clone HASS installer"
    git clone https://github.com/liviuflore/home-assistant-installer.git
    cd home-assistant-installer
fi

fab deploy:venv=$virtualenv,ssl=$usessl,configuration=$config_path -H $target_host -u $target_user 2>&1 | tee installation_report.txt

exit
