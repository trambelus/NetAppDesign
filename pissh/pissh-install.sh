#!/bin/sh

sudo update-rc.d -f pissh remove
sudo cp pissh-pi.sh /etc/init.d/pissh
sudo update-rc.d pissh defaults
