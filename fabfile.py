########################################
# Fabfile to:
#    - deploy supporting HA components
#    - deploy HA
########################################

# Import Fabric's API module
from fabric.api import *
import fabric.contrib.files
import time
import os


env.hosts = ['localhost']
#env.user = "pi"
#env.password = "raspberry"
env.user = "vagrant"
env.password = "vagrant"
env.warn_only = True
#pi_hardware = os.uname()[4]

#######################
## Core server setup ##
#######################

def install_start():
    """ Notify of install start """
    time.sleep(10)
    print("HASS installer is starting...")
    time.sleep(5)
    
    # setup base dev dir
    with cd("/srv"):
        sudo("mkdir hass")
        sudo("chown hass hass")
        with cd("hass"):
            sudo("mkdir -p src")
            sudo("chown hass:hass src")
            
def install_syscore():
    """ Download and install Host Dependencies. """
    sudo("apt-get install -y python-pip")
    sudo("apt-get install -y python3")
    sudo("apt-get install -y python3-pip")
    sudo("apt-get install -y git")
    sudo("apt-get install -y libssl-dev")
    sudo("apt-get install -y cmake")
    sudo("apt-get install -y libc-ares-dev")
    sudo("apt-get install -y uuid-dev")
    sudo("apt-get install -y daemon")
    sudo("apt-get install -y curl")
    #sudo("apt-get install -y libgnutls28-dev")
    #sudo("apt-get install -y libgnutlsxx28")
    sudo("apt-get install -y libgnutls-dev")
    sudo("apt-get install -y nmap")
    sudo("apt-get install -y net-tools")
    #sudo("apt-get install -y sudo")
    #sudo("apt-get install -y libglib2.0-dev")
    #sudo("apt-get install -y cython3")
    sudo("apt-get install -y libudev-dev")
    #sudo("apt-get install -y python3-sphinx")
    sudo("apt-get install -y python3-setuptools")
    #sudo("apt-get install -y libxrandr-dev")
    sudo("apt-get install -y python-dev")
    #sudo("apt-get install -y swig")



def setup_homeassistant(venv = 0):
    """ Install Home Assistant"""
    sudo("pip3 install --upgrade pip")
    
    # setup users
    sudo("useradd --system hass")
    sudo("usermod -G dialout -a hass")
    sudo("usermod -G video -a hass")
    sudo("usermod -d /home/hass hass")
    
    # setup dirs
    with cd("/home"):
        sudo("mkdir -p hass")
        sudo("mkdir -p /home/hass/.homeassistant")
        sudo("chown hass:hass hass")
        
    if venv == 0:
        hass_bin = "/usr/bin/hass"
    else:
        hass_bin = "/srv/hass/venv/bin/hass"
        # Install and create home-assistant VirtualEnv
        sudo("pip3 install virtualenv")
        with cd("/srv/hass"):
            sudo("virtualenv -p python3 venv", user="hass")
        # Activate Virtualenv
        sudo("source /srv/hass/venv/bin/activate", user="hass")

    # Install Home-Assistant
    sudo("pip3 install homeassistant", user="hass")

    # TODO: setup /home/hass/.homeassistant/configuration.yaml
    
    with open("home-assistant.service.template", "rt") as fin:
        with open("home-assistant.service", "wt") as fout:
            for line in fin:
                fout.write(line.replace('[HASS_BIN]', hass_bin))

    with cd("/etc/systemd/system/"):
        put("home-assistant.service", "home-assistant.service", use_sudo=True)
    with settings(sudo_user='hass'):
        sudo(hass_bin + " --script ensure_config --config /home/hass/.homeassistant")

    sudo("systemctl enable home-assistant.service")
    sudo("systemctl daemon-reload")

def setup_mosquitto():
    """ Install Mosquitto w/ websockets"""
    sudo("useradd mosquitto")
    with cd("/var/lib/"):
        sudo("mkdir mosquitto")
        sudo("chown mosquitto:mosquitto mosquitto")
    with cd("/srv/hass/src"):
        sudo("curl -O http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key")
        sudo("apt-key add mosquitto-repo.gpg.key")
        with cd("/etc/apt/sources.list.d/"):
            sudo("curl -O http://repo.mosquitto.org/debian/mosquitto-jessie.list")
            sudo("apt-get update")
            sudo("apt-cache search mosquitto")
            sudo("apt-get install -y mosquitto mosquitto-clients")
            with cd("/etc/mosquitto"):
                put("mosquitto.conf", "mosquitto.conf", use_sudo=True)
                sudo("touch pwfile")
                sudo("chown mosquitto: pwfile")
                sudo("chmod 0600 pwfile")
                sudo("sudo mosquitto_passwd -b pwfile pi raspberry")
                sudo("sudo chown mosquitto: mosquitto.conf")

def setup_libmicrohttpd():
    """ Build and install libmicrohttpd """
    with cd("/srv/hass/src"):
        sudo("mkdir libmicrohttpd")
        sudo("chown hass:hass libmicrohttpd")
        sudo("curl -O ftp://ftp.gnu.org/gnu/libmicrohttpd/libmicrohttpd-latest.tar.gz", user="hass")
        sudo("tar zxvf libmicrohttpd-latest.tar.gz")
        with cd("$(ls -d */|head -n 1)"):
            sudo("./configure")
            sudo("make")
            sudo("make install")


#############
## Deploy! ##
#############

def deploy(venv = 0):

    install_start()
    install_syscore()
    setup_mosquitto()
    setup_homeassistant(venv)
    #setup_libmicrohttpd()
    #reboot()
