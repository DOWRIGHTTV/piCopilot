#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Eventually the idrop web gui will have a password.  That is where this comes into play

pre-reqs:
  psutil

/etc/systemd/system/kwatcher.service
[Unit]
Description=Monitor kwatcher for pgsql hiccups
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/kWatcher.py <IP>
TimeoutStartSec=0

[Install]
WantedBy=default.target
"""

import getpass
import logging
import os
import psutil
import sys
import time
from configparser import ConfigParser

class Watcher(object):
    def __init__(self):
        self.parser = ConfigParser()
        parser.read('ksnarf.ini')
        self.hashDict = {}
        for (k, v) in parser.items(users):
            self.hashDict.update({k: v})

        ## Drop to the directory
        os.chdir('/opt/piCopilot-idrop')


    def hashCheck(self, pWord, stdOut = False):
        result = hashlib.sha512(pWord.encode())
        if stdOut is True:
            print(result.hexdigest())
        return result


    def watcher(self):
        running = False
        try:
            for i in psutil.process_iter():
                if 'kSniff.sh' in i.cmdline():
                    running = True
        except Exception as E:
            print(E)
            logging.warn(E)

        if running is False:
            msg = 'kSnarf not running, kickstarting'
            print(msg)
            logging.warn(msg)
            os.system('supervisorctl start kSniff')
"""
./kSnarf.py -i <NIC> -m ids --psql --host '{0}' --user '{1}' >' --id '<Enclave ID>' --cache 30 --recover --debug 1
/usr/bin/python3 /opt/piCopilot-idrop/kSnarf.py -d rt2800usb-NEH\
 --hop 3\
 --host '127.0.0.1'\
 --psql\
 --user root\
 --password idrop\
 -c '1 2 3 4 5 6 7 8 9 10 11'\
 -i wlan1mon\
 -m listen\
 -p 'probes'
"""




if __name__ == '__main__':
    w = Watcher()
    logging.basicConfig(format='%(asctime)s %(message)s', filename = '/var/log/messages', level = logging.INFO)
    msg = 'kWatcher - kWatcher.py started'
    print(msg)
    logging.info(msg)
    w.user = input('Username?\n')
    w.password = getpass.getpass('Password?\n')
    proceed = False
    pHash = w.hashDict.get(w.user)
    cHash = w.hashCheck(pWord)
    if cHash == pHash:
        proceed = True
    if proceed is True:
        w.host = w.parser.get('ksnarf', 'host')
        w.fwip = w.parser.get('ksnarf', 'fwip')
        w.id = w.parser.get('ksnarf', 'id')
        w.driver = w.parser.get('ksnarf', 'driver')
        w.nic = w.parser.get('ksnarf', 'nic')

        while True:
            w.watcher()
            time.sleep(10)
    else:
        print('bad pass')
        sys.exit(1)
