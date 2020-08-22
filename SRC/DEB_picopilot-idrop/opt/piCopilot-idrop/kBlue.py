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


    def onlyCare(self):
        """Only load parsers for what we care about"""
        q=[scapy.layers.bluetooth4LE.BTLE,
           scapy.layers.bluetooth4LE.BTLE_RF,
           scapy.layers.bluetooth4LE.BTLE_ADV,
           scapy.layers.bluetooth4LE.EIR_Hdr,
           scapy.layers.bluetooth4LE.BTLE_ADV_NONCONN_IND]
        conf.layers.filter(q)


    def pgsqlFilter(self):
        def snarf(packet):
            if packet.haslayer(BTLE_ADV_NONCONN_IND):

                ### THIS IS ENTRY POINT
                if self.seenTest(packet) is False:
                    ### CLEARED HOT TO LOG

                    epoch, lDate, lTime = self.timer()
                    tStamp = str(lDate) + ' ' + str(lTime)
                    try:
                        tMac = packet[BTLE_ADV_NONCONN_IND].AdvA
                        pSignal = packet[BTLE_RF].signal
                        pNoise = packet[BTLE_RF].noise

                        ## Update the db
                        self.db.execute("""
                                        INSERT INTO blue (epoch,
                                                          pi_timestamp,
                                                          date,
                                                          time,
                                                          mac,
                                                          signal,
                                                          noise)
                                                     VALUES (%s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s,
                                                             %s);
                                                 """, (epoch,
                                                       str(lDate) + ' ' + str(lTime),
                                                       lDate,
                                                       lTime,
                                                       tMac,
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
                                                       mac TEXT,
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
        try:
            p = (packet[BTLE_ADV_NONCONN_IND].AdvA,
                 packet[BTLE_RF].signal,
                 packet[BTLE_RF].noise)

            ## Figure out if this combo has been seen before
            if p not in self.unity.seenDict:
                self.unity.seenDict.update({p: (1, time.time())})
                #print ('PASS TIMER')
                return False

            ## Has been seen, now check time
            else:
                lastTime = self.unity.seenDict.get(p)[1]
                lastCount = self.unity.seenDict.get(p)[0]
                if (time.time() - lastTime) > self.unity.seenMaxTimer:

                    ## Update delta timestamp
                    self.unity.seenDict.update({p: (lastCount + 1, time.time())})
                    #print ('PASS TIMER')
                    return False
                else:
                    #print ('FAIL TIMER')
                    return True
        except:
            pass

    def timer(self):



        epoch = int(time.time())                                          ## Store the epoch in UTC
        lDate = time.strftime('%Y-%m-%d', time.localtime())               ## Store the date in local tz
        lTime = time.strftime('%H:%M:%S', time.localtime())               ## Store the time in local tz
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
