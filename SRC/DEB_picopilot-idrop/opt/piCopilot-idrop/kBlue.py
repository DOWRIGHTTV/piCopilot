#!/usr/bin/python3

"""
kBlue -- Sniff teh bluetooths
"""

import argparse
import netaddr
import os
import re
import time
import signal
import sqlite3 as lite
import sys
import psycopg2
from lib.unifier import Unify
from scapy.all import *
from subprocess import Popen

class Blue(object):
    """Handle all things for bluetooth"""

    def __init__(self, args):
        ##Do some filtering to ignore parsing we don't need
        self.onlyCare()
        self.pipeSleep = 20
        self.availPipes = ['/mnt/usb_storage/bluesPipe-1',
                           '/mnt/usb_storage/bluesPipe-2']

        ## Connect to the db
        self.con, self.db, self.dbName = self.pgsqlPrep()
        self.PRN = self.pgsqlFilter()


    def choiceMaker(self, packet):
        proceed = False
        for choice in self.choices[:-4]:
            if packet.haslayer(choice):
                self.chosen = str(choice).split('.')[-1].split("'")[0]                ## Change logic before threading
                return True
        return False


    def onlyCare(self):
        """Only load parsers for what we care about
        self.choices[:-4] is the list of objects we rip from currently
        """
        self.choices = [scapy.layers.bluetooth4LE.BTLE_ADV_IND,
                        scapy.layers.bluetooth4LE.BTLE_ADV_NONCONN_IND,
                        scapy.layers.bluetooth4LE.BTLE_ADV_SCAN_IND,
                        scapy.layers.bluetooth4LE.BTLE_SCAN_REQ,
                        scapy.layers.bluetooth4LE.BTLE_SCAN_RSP,
                        scapy.layers.bluetooth4LE.BTLE_ADV_DIRECT_IND,
                        scapy.layers.bluetooth4LE.BTLE,
                        scapy.layers.bluetooth4LE.BTLE_RF,
                        scapy.layers.bluetooth4LE.BTLE_ADV,
                        scapy.layers.bluetooth4LE.EIR_Hdr]
        conf.layers.filter(self.choices)


    def pgsqlFilter(self):
        def snarf(packet):
            epoch, lDate, lTime = self.timer()

            ## Only test if known MAC field(s) exists
            if self.choiceMaker(packet) is True:

                ### THIS IS ENTRY POINT
                if self.seenTest(packet) is False:

                    ### CLEARED HOT TO LOG
                    tStamp = str(lDate) + ' ' + str(lTime)
                    try:
                        pSignal = packet[BTLE_RF].signal
                        pNoise = packet[BTLE_RF].noise

                        ## Update the db
                        self.db.execute("""
                                        INSERT INTO blue (epoch,
                                                          pi_timestamp,
                                                          date,
                                                          time,
                                                          parent,
                                                          adva,
                                                          inita,
                                                          scana,
                                                          signal,
                                                          noise)
                                                     VALUES (%s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s);
                                                 """, (epoch,
                                                       tStamp,
                                                       lDate,
                                                       lTime,
                                                       self.bTuple[0],
                                                       self.bTuple[1],
                                                       self.bTuple[2],
                                                       self.bTuple[3],
                                                       pSignal,
                                                       pNoise))
                    except Exception as E:
                        print(E)
        return snarf


    def pgsqlPrep(self):
        """ Connect and prep the pgsql db"""
        try:
            cStr = "dbname='idrop' user='%s' host='%s' password='%s'" % ('root', '127.0.0.1', 'idrop')
            con = psycopg2.connect(cStr)
            con.autocommit = True
            db = con.cursor()

            ## db prep
            db.execute("""
                       CREATE TABLE IF NOT EXISTS blue(epoch REAL,
                                                       pi_timestamp TIMESTAMPTZ,
                                                       date TEXT,
                                                       time TEXT,
                                                       parent TEXT,
                                                       adva TEXT,
                                                       inita TEXT,
                                                       scana TEXT,
                                                       signal INT,
                                                       noise INT);
                       """)
        except Exception as E:
            print ("I am unable to connect to the database idrop")
            print(E)
            sys.exit(1)
        dbName = 'idrop'

        return (con, db, dbName)


    ### Move to a common library with snarf.py
    def seenTest(self, packet):
        """Gather essential identifiers for "have I seen this packet" test

        Return False to continue with this test.  "seenTest", if not seen,
        then continue

        Will return False if the delta of now and previous timestamp
        for a given frame are > self.unity.seenMaxTimer {Default 30 seconds},
        otherwise we ignore, and thus by ignoring, we do not clog up the logs

        Create a table, and store this data so we can query on the fly
            - only with psql
        """
        self.bTuple = None                                                      ## Rework if threading
        try:
            if self.chosen == 'BTLE_ADV_IND':
                self.bTuple = (self.chosen,
                               packet[BTLE_ADV_IND].AdvA,
                               None,
                               None)
            if self.chosen == 'BTLE_ADV_NONCONN_IND':
                self.bTuple = (self.chosen,
                               packet[BTLE_ADV_NONCONN_IND].AdvA,
                               None,
                               None)
            if self.chosen == 'BTLE_ADV_SCAN_IND':
                self.bTuple = (self.chosen,
                               packet[BTLE_ADV_SCAN_IND].AdvA,
                               None,
                               None,)
            if self.chosen == 'BTLE_SCAN_REQ':
                self.bTuple = (self.chosen,
                               packet[BTLE_SCAN_REQ].AdvA,
                               None,
                               packet[BTLE_SCAN_REQ].ScanA)
            if self.chosen == 'BTLE_SCAN_RSP':
                self.bTuple = (self.chosen,
                               packet[BTLE_SCAN_RSP].AdvA,
                               None,
                               None)
            if self.chosen == 'BTLE_ADV_DIRECT_IND':
                self.bTuple = (self.chosen,
                               packet[BTLE_ADV_DIRECT_IND].AdvA,
                               None,
                               packet[BTLE_ADV_DIRECT_IND].InitA)
        except Exception as E:
            print(E)

        ## Figure out if this combo has been seen before
        if self.bTuple is not None:
            if self.bTuple not in self.unity.seenDict:
                self.unity.seenDict.update({self.bTuple: (1, time.time())})

                # print("I AM NOT FOUND")
                return False

            ## Has been seen, now check time
            else:
                lastTime = self.unity.seenDict.get(self.bTuple)[1]
                lastCount = self.unity.seenDict.get(self.bTuple)[0]
                if (time.time() - lastTime) > self.unity.seenMaxTimer:

                    ## Update delta timestamp
                    self.unity.seenDict.update({self.bTuple: (lastCount + 1, time.time())})
                    # print ('PASS TIMER')
                    return False
                else:
                    # print ('FAIL TIMER')
                    return True


    def timer(self):
        epoch = int(time.time())                                                ## Store the epoch in UTC
        lDate = time.strftime('%Y-%m-%d', time.localtime(epoch))                ## Store the date in local tz
        lTime = time.strftime('%H:%M:%S', time.localtime(epoch))                ## Store the time in local tz
        return epoch, lDate, lTime


    def main(self, args):
        ## Unify it up
        self.unity = Unify(args, control = None, kBlue = True)
        self.unity.seenMaxTimer = 30
        self.unity.seenDict = {}

        while True:
            for pipe in self.availPipes:
                print('sniffing pipe {0}'.format(pipe))
                self.pipePush(pipe, self.pipeSleep)
                p = sniff(offline = '{0}'.format(pipe), prn = self.PRN)                  ## need to thread and move on.
                time.sleep(.1)
        con.close()


    def pipePush(self, pipe, sVal):
        bPipe = os.system('/usr/bin/timeout {0} /usr/bin/ubertooth-btle -f -q {1} 1>/dev/null'.format(sVal, pipe))


def crtlC(args):
    """Handle CTRL+C."""
    def tmp(signal, frame):
        sys.exit(0)
    return tmp

if __name__ == '__main__':
    ## ARGUMENT PARSING
    parser = argparse.ArgumentParser(description = 'kBlue')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('--pgsql',
                       action = 'store_true',
                       help = 'kBlue pgsql mode')
    args = parser.parse_args()

    ## ADD SIGNAL HANDLER
    signal_handler = crtlC(args)
    signal.signal(signal.SIGINT, signal_handler)

    ## Launch
    bl = Blue(args)
    bl.main(args)
