#!/bin/bash

## Verify we have mon mode
airmon-ng start wlan1

## Launch kSnarf
/usr/bin/python3 /opt/piCopilot-idrop/kSnarf.py -d rt2800usb-NEH\
 --hop 3\
 --host '127.0.0.1'\
 --psql\
 --user root\
 --password idrop\
 --db idrop\
 -c '1 2 3 4 5 6 7 8 9 10 11'\
 -i wlan1mon\
 -m listen\
 -p 'probes'
