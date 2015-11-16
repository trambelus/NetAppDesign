#!/usr/bin/env python

script = """
#!/bin/sh
# /etc/init.d/pissh-pi.sh
sleep 15
wget "http://jenna.xen.prgmr.com:5000/pissh/push?ip=$(ifconfig wlan0 | awk '/inet addr/{print substr($2,6)}')&id={}" -O /dev/null &>/dev/null
exit 0
"""

