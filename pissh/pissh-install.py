#!/usr/bin/env python

script = """
#!/bin/sh
# /etc/init.d/pissh-pi.sh
### BEGIN INIT INFO
# Provides:          noip
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Simple script to start a program at boot
# Description:       A simple script from www.stuffaboutcode.com which will start / stop a program a boot / shutdown.
### END INIT INFO

sleep 15
wget "http://jenna.xen.prgmr.com:5000/pissh/push?ip=$(ifconfig wlan0 | awk '/inet addr/{print substr($2,6)}')&id={}" -O /dev/null &>/dev/null
exit 0
"""

