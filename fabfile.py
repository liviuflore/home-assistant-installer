########################################
# Fabfile to:
#    - deploy supporting HA components
#    - deploy HA
#    - usage: fab deploy:configuration=/vagrant/hassconfig,venv=False,ssl=True -H localhost 2>&1
########################################

# Import Fabric's API module
from fabric.api import *
import fabric.contrib.files
import time
import os
import platform


#env.hosts = ['localhost']
env.warn_only = False

use_virtualenv = False
use_configuration = ""
use_ssl = False

#######################
## Core server setup ##
#######################

def install_start():
    """ Notify of install start """
    time.sleep(2)
    print("HASS installer is starting...")
    time.sleep(1)
    
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
    #sudo("apt-get install -y libgnutls-dev")
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



def setup_homeassistant():
    """ Install Home Assistant"""
    sudo("pip3 install --upgrade pip")
    
    if use_virtualenv == 0:
        hass_bin = "/usr/local/bin/hass"
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
        
    # Install Home-Assistant
    if use_virtualenv == 0:
        sudo("pip3 install homeassistant")
    else:
        sudo("pip3 install homeassistant", user=hass_user)

    # make default configuration
    with settings(sudo_user=hass_user):
        sudo(hass_bin + " --script ensure_config --config /home/" + hass_user + "/.homeassistant")

    # install configuration if provided
    if use_configuration != "":
        put(use_configuration + "/*", "/home/" + hass_user + "/.homeassistant")

    # add custom hass variable loading if exists
    hass_bin = "if [ -f /home/" + hass_user + "/.homeassistant/vars.sh ]; then source /home/" + hass_user + "/.homeassistant/vars.sh; fi && " + hass_bin
    
    # create autostart file
    if float(platform.dist()[1]) >= 15.04:
        with open("home-assistant.service.template", "rt") as fin:
            with open("home-assistant.service", "wt") as fout:
                for line in fin:
                    fout.write(line.replace('[HASS_BIN]', hass_bin).replace('[HASS_USER]', hass_user))
        with cd("/etc/systemd/system/"):
            put("home-assistant.service", "home-assistant.service", use_sudo=True)
        sudo("systemctl enable home-assistant.service")
        sudo("systemctl daemon-reload")
    else:
        # TODO: make upstart script
        with open("HAstart.sh", "wt") as fout:
            fout.write("#!/bin/bash\n") 
            fout.write(hass_bin + " --config /home/" + hass_user + "/.homeassistant\n")
        put("HAstart.sh", "/home/" + hass_user)

def setup_mosquitto():
    """ Install Mosquitto w/ websockets w/ ssl"""
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
            
                if use_ssl:
                    sudo("mkdir -p /srv/mosquitto")
                    sudo("chown mosquitto:mosquitto /srv/mosquitto")
                    with cd("/srv/mosquitto"):
                        sudo("wget -Nnv https://raw.githubusercontent.com/owntracks/tools/master/TLS/generate-CA.sh", user="mosquitto")
                        sudo("chmod +x ./generate-CA.sh")
                        sudo("./generate-CA.sh")
                        sudo("cp ca.crt /etc/mosquitto/certs")
                        sudo("cp " + platform.node() + ".* /etc/mosquitto/certs")
                        
                with open("mosquitto.conf.template", "rt") as fin:
                    with open("mosquitto.conf", "wt") as fout:
                        for line in fin:
                            fout.write(line.replace('[HOSTNAME]', platform.node()))
                put("mosquitto.conf", "mosquitto.conf", use_sudo=True)
                sudo("touch pwfile")
                sudo("chown mosquitto: pwfile")
                sudo("chmod 0600 pwfile")
                sudo("sudo mosquitto_passwd -b pwfile " + env.user + " " + env.password)
                sudo("sudo chown mosquitto: mosquitto.conf")


def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError("Cannot covert {} to a bool".format(s))

#############
## Deploy! ##
#############

def deploy(venv = str(use_virtualenv), configuration = use_configuration, ssl = str(use_ssl)):
    
    global use_virtualenv; use_virtualenv = str_to_bool(venv)
    global use_configuration; use_configuration = configuration
    global use_ssl; use_ssl = str_to_bool(ssl)
    print("Install Home Assistant")
    print("  virtual environment [%r]" % use_virtualenv)
    print("  configuration       [%s]" % use_configuration)
    print("  ssl                 [%r]" % use_ssl)
    print("  host                [%s]" % env.host)
    print("  user                [%s]" % env.user)
    
    install_start()
    install_syscore()
    setup_mosquitto()
    setup_homeassistant()
    
    #reboot()
