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
env.warn_only = False
#pi_hardware = os.uname()[4]

#######################
## Core server setup ##
#######################

def install_start():
    """ Notify of install start """
    time.sleep(2)
    print("HASS installer is starting...")
    time.sleep(1)
    
    # setup base dev dir
    #with cd("/srv"):
    #    sudo("mkdir -p hass")
    #    #sudo("chown hass hass")
    #    with cd("hass"):
    #        sudo("mkdir -p src")
    #        #sudo("chown hass:hass src")
            
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
    sudo("apt-get install -y sudo")
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
    
    if venv == 0:
        hass_bin = "/usr/bin/hass"
        hass_user = env.user
    else:
        hass_bin = "/srv/hass/venv/bin/hass"
        hass_user = "hass"
        
        # create user
        sudo("id -u hass &>/dev/null || useradd --system -rm hass")

        # create hass venv dir
        with cd("/srv"):
            sudo("mkdir -p hass")
            sudo("chown -R hass hass")
        
        # Install and create home-assistant VirtualEnv
        sudo("pip3 install virtualenv")
        with cd("/srv/hass"):
            sudo("virtualenv -p python3 venv", user="hass")
            
        # Activate Virtualenv
        sudo("source /srv/hass/venv/bin/activate", user="hass")

    sudo("usermod -G dialout -a " + hass_user)
    sudo("usermod -G video -a " + hass_user)

    # create config dir
    with cd("/home/" + hass_user):
        sudo("mkdir -p /home/" + hass_user + "/.homeassistant", user=hass_user)
        
    # TODO: setup /home/hass/.homeassistant/configuration.yaml

    # Install Home-Assistant
    if venv == 0:
        sudo("pip3 install homeassistant")
    else:
        sudo("pip3 install homeassistant", user=hass_user)
    
    with open("home-assistant.service.template", "rt") as fin:
        with open("home-assistant.service", "wt") as fout:
            for line in fin:
                fout.write(line.replace('[HASS_BIN]', hass_bin).replace('[HASS_USER]', hass_user))

    with cd("/etc/systemd/system/"):
        put("home-assistant.service", "home-assistant.service", use_sudo=True)
    with settings(sudo_user='hass'):
        sudo(hass_bin + " --script ensure_config --config /home/" + hass_user + "/.homeassistant")

    sudo("systemctl enable home-assistant.service")
    sudo("systemctl daemon-reload")

def setup_mosquitto():
    """ Install Mosquitto w/ websockets"""
    sudo("id -u mosquitto &>/dev/null || useradd mosquitto")
    with cd("/var/lib/"):
        sudo("mkdir -p mosquitto")
        sudo("chown mosquitto:mosquitto mosquitto")

    with cd("~"):
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
                sudo("sudo mosquitto_passwd -b pwfile " + env.user + " " + env.password)
                sudo("sudo chown mosquitto: mosquitto.conf")


#############
## Deploy! ##
#############

def deploy(venv = 0):
    print("Install Home Assistant in virtual env [%d]" % venv)
    install_start()
    install_syscore()
    setup_mosquitto()
    setup_homeassistant(venv)
    #reboot()
