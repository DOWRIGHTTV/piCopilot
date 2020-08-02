#!/bin/bash

## Verify we have mon mode
airmon-ng start wlan1

## Launch kSnarf
# /usr/bin/python2 /opt/piCopilot-idrop/kSnarf.py -d rt2800usb -i wlan1mon -p 'dhcp probes' -m listen -c '1 2 3 4 5 6 7 8 9 10 11' --hop 3
/usr/bin/python2 /opt/piCopilot-idrop/kSnarf.py -d rt2800usb-NEH\
 --hop 3\
 --psql\
 --user root\
 --password idrop\
 -c '1 2 3 4 5 6 7 8 9 10 11'\
 -i wlan1mon\
 -m listen\
 -p 'dhcp probes'
