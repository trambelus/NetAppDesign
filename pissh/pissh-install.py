#!/usr/bin/env python

import argparse
import os

def main():
	parser = argparse.ArgumentParser("Installer for PiSSH IP announcer into Raspberry Pi startup")
	parser.add_argument("id", help='string to identify this device on the server')
	args = parser.parse_args()
	pi_id = args.id

	script = """#!/bin/sh
# /etc/init.d/pissh
### BEGIN INIT INFO
# Provides:          PiSSH
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Announces this pi's ip to a server
# Description:       Sends this device's local wlan0 IP address to the PiSSH server, and clears it on shutdown.
### END INIT INFO

case "$1" in
	start)
		sleep 5
		ipaddr=$(ifconfig eth0 | awk '/inet addr/{{print substr($2,6)}}')
		echo "PiSSH: Sending IP $ipaddr to server"
		wget "http://jenna.xen.prgmr.com:5281/pissh/push?ip=$ipaddr&id={0}" -O /dev/null &>/dev/null
		exec home/pi/ustat/camera.py
		;;
	stop)
		echo "PiSSH: Clearing entry from server"
		wget "http://jenna.xen.prgmr.com:5281/pissh/clear?id={0}" -O /dev/null &>/dev/null
		;;
	*)
		echo "Usage: /etc/init.d/pissh {{start|stop}}"
		exit 1
		;;
esac
exit 0
""".format(pi_id)

	try:
		os.system('sudo update-rc.d -f pissh remove') # Remove previous services called 'pissh', just in case
		with open('/etc/init.d/pissh', 'w') as f:	# (over)write the file at this location
			f.write(script)
		os.system('sudo chmod +x /etc/init.d/pissh')
		os.system('sudo update-rc.d pissh defaults') # Install this service
	except Exception as ex:
		print("Something went wrong. Did you remember to sudo?")
		raise ex

if __name__ == '__main__':
	main()
