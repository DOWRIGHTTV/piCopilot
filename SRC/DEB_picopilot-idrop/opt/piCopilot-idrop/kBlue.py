#!/usr/bin/python3

"""
Temporary integration meld for kBlue to idrop
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
from scapy.all import *
from subprocess import Popen

def crtlC(args):
    """Handle CTRL+C."""
    def tmp(signal, frame):
        sys.exit(0)
    return tmp

def sqlitePrep():
    """Connect and prep the db"""
    sqlName ='teeth.sqlite3'
    dbName = 'blue'
    con = lite.connect(sqlName)
    db = con.cursor()

    ## sqlite3 table create
    db.execute("""
               CREATE TABLE IF NOT EXISTS {0}(tstamp TEXT,
                                              mac TEXT,
                                              signal INTEGER,
                                              noise INTEGER);
               """.format(dbName))
    return (con, db, dbName)


def pgsqlPrep():
    """ Connect and prep the pgsql db"""
    try:
        # cStr = "dbname='idrop' user='%s' host='%s' password='%s'" % (unity.args.user, unity.args.host, unity.args.password)
        cStr = "dbname='idrop' user='%s' host='%s' password='%s'" % ('root', '127.0.0.1', 'idrop')
        con = psycopg2.connect(cStr)
        con.autocommit = True
        db = con.cursor()

        ## db prep
        db.execute("""
                   CREATE TABLE IF NOT EXISTS blue(epoch INT,
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


def onlyCare():
    """Only load parser for what we care about"""
    q=[scapy.layers.bluetooth4LE.BTLE,
       scapy.layers.bluetooth4LE.BTLE_RF,
       scapy.layers.bluetooth4LE.BTLE_ADV,
       scapy.layers.bluetooth4LE.EIR_Hdr,
       scapy.layers.bluetooth4LE.BTLE_ADV_NONCONN_IND]
    conf.layers.filter(q)


def pgsqlFilter(db, dbName):
    def snarf(packet):
        if packet.haslayer(BTLE_ADV_NONCONN_IND):
            epoch, lDate, lTime = timer()
            tStamp = str(lDate) + ' ' + str(lTime) + '-05'
            try:
                tMac = packet[BTLE_ADV_NONCONN_IND].AdvA
                pSignal = packet[BTLE_RF].signal
                pNoise = packet[BTLE_RF].noise

                ## sqlite3 table INSERT
                db.execute("""
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
                                          str(lDate) + ' ' + str(lTime) + '-05',
                                          lDate,
                                          lTime,
                                          tMac,
                                          pSignal,
                                          pNoise))

            except Exception as E:
                print(E)
    return snarf


def timer():
    epoch = int(time.time())                                          ## Store the epoch in UTC
    lDate = time.strftime('%Y-%m-%d', time.localtime())               ## Store the date in local tz
    lTime = time.strftime('%H:%M:%S', time.localtime())               ## Store the time in local tz
    return epoch, lDate, lTime


# def seenTest(self, packet):
#     """Gather essential identifiers for "have I seen this packet" test
#
#     Return False to continue with this test.  "seenTest", if not seen,
#     then continue
#
#     Will return False if the delta of now and previous timestamp
#     for a given frame are > self.unity.seenMaxTimer {Default 30 seconds},
#     otherwise we ignore, and thus by ignoring, we do not clog up the logs
#
#     Create a table, and store this data so we can query on the fly
#         - only with psql
#     """
#     try:
#         p = (packet[Dot11].subtype,
#              packet[Dot11].type,
#              packet[Dot11].FCfield,
#              packet[Dot11].addr1,
#              packet[Dot11].addr2,
#              packet[Dot11].addr3,
#              packet[Dot11].addr4)
#
#         ## Figure out if this combo has been seen before
#         if p not in self.unity.seenDict:
#             self.unity.seenDict.update({p: (1, time.time())})
#             #print ('PASS TIMER')
#
#             ## Add if psql
#             if self.unity.args.psql is True:
#                 pType = self.unity.PE.conv.symString(packet[Dot11], 'type')
#                 subType = self.subParser(packet)
#                 fcField = self.unity.PE.conv.symString(packet[Dot11], 'FCfield')
#                 try:
#                     self.cap.db.execute("""
#                                         INSERT INTO uniques (pid,
#                                                              epoch,
#                                                              pi_timestamp,
#                                                              date,
#                                                              time,
#                                                              type,
#                                                              subtype,
#                                                              FCfield,
#                                                              addr1,
#                                                              addr2,
#                                                              addr3,
#                                                              addr4)
#                                                      VALUES (%s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s,
#                                                              %s);
#                                         """, (self.unity.logDict.get('total'),
#                                               self.unity.epoch,
#                                               str(self.unity.lDate) + ' ' + str(self.unity.lTime) + '-05',
#                                               self.unity.lDate,
#                                               self.unity.lTime,
#                                               pType,
#                                               subType,
#                                               fcField,
#                                               packet.addr1,
#                                               packet.addr2,
#                                               packet.addr3,
#                                               packet.addr4))
#                 except Exception as E:
#                     print (E)
#
#             return False
#
#         ## Has been seen, now check time
#         else:
#             lastTime = self.unity.seenDict.get(p)[1]
#             lastCount = self.unity.seenDict.get(p)[0]
#             if (time.time() - lastTime) > self.unity.seenMaxTimer:
#
#                 ## Update delta timestamp
#                 self.unity.seenDict.update({p: (lastCount + 1, time.time())})
#
#                 ### Should pass this information along to a DB for consumption `p` analysis wise
#
#
#                 #print ('PASS TIMER')
#                 return False
#             else:
#                 #print ('FAIL TIMER')
#                 return True
#     except:
#         pass


def sqliteFilter(db, dbName):
    def snarf(packet):
        if packet.haslayer(BTLE_ADV_NONCONN_IND):
            tNow = time.localtime()
            lDate = time.strftime('%Y-%m-%d', tNow)
            lTime = time.strftime('%H:%M:%S', tNow)
            tStamp = str(lDate) + ' ' + str(lTime) + '-05'
            try:
                tMac = packet[BTLE_ADV_NONCONN_IND].AdvA
                pSignal = packet[BTLE_RF].signal
                pNoise = packet[BTLE_RF].noise

                ## sqlite3 table INSERT
                print(tStamp,tMac,pSignal,pNoise)
                db.execute("""
                           INSERT INTO `{0}` VALUES(?,
                                                    ?,
                                                    ?,
                                                    ?);
                           """.format(dbName), (str(lDate) + ' ' + str(lTime) + '-05',
                                                tMac,
                                                pSignal,
                                                pNoise))
            except Exception as E:
                print(E)
    return snarf


def main(args):
    ## Do some filtering to ignore parsing we don't need
    onlyCare()
    pipeSleep = 20
    availPipes = ['/mnt/usb_storage/bluesPipe-1',
                  '/mnt/usb_storage/bluesPipe-2']

    ## Connect to the db
    if args.sqlite is True:
        con, db, dbName = sqlitePrep()
        PRN = sqliteFilter(db, dbName)
    else:
        con, db, dbName = pgsqlPrep()
        PRN = pgsqlFilter(db, dbName)

    while True:
        for pipe in availPipes:
            print('sniffing pipe {0}'.format(pipe))
            pipePush(pipe, pipeSleep)
            p = sniff(offline = '{0}'.format(pipe), prn = PRN)                  ## need to thread and move on.
            time.sleep(.1)
    con.close()


def pipePush(pipe, sVal):
    bPipe = os.system('/usr/bin/timeout {0} /usr/bin/ubertooth-btle -f -q {1} 1>/dev/null'.format(sVal, pipe))

if __name__ == '__main__':

    ## ARGUMENT PARSING
    parser = argparse.ArgumentParser(description = 'kBlue')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('--sqlite',
                       action = 'store_true',
                       help = 'kBlue sqlite3 mode')
    group.add_argument('--pgsql',
                       action = 'store_true',
                       help = 'kBlue pgsql mode')
    args = parser.parse_args()

    ## ADD SIGNAL HANDLER
    signal_handler = crtlC(args)
    signal.signal(signal.SIGINT, signal_handler)

    ## Launch
    main(args)
