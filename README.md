# home-assistant-installer

The [Custom Raspberry Pi All-In-One Installer] deploys a complete Home Assistant server including support for MQTT with websockets.
Based on https://github.com/home-assistant/fabric-home-assistant

Requirement: Raspberry Pi with a fresh installation of [Raspbian Jessie/Jessie Lite](https://www.raspberrypi.org/downloads/raspbian/) connected to your network.

How To:
*  Login to Raspberry Pi. For example with `ssh pi@your_raspberry_pi_ip`
*  Run the following command

```bash
$ wget -Nnv https://raw.githubusercontent.com/liviuflore/home-assistant-installer/master/hass_installer.sh && bash hass_installer.sh
```
*Note this command is one line and not run as sudo*

*Windows Users* - Please note that after running the installer, you will need to modify settings allowing you to "switch users" to edit your configuration files. The needed change within WinSCP is: Environment -> SCP/Shell -> Shell and set it to `sudo su -`.
