#!/bin/bash

wget "http://jenna.xen.prgmr.com:5000/pissh/push?ip=$(ifconfig wlan0 | awk '/inet addr/{print substr($2,6)}')&id=T25Pi"
