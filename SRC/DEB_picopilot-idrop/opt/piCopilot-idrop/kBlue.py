#!/usr/bin/python3

"""
Temporary integration meld for kBlue to idrop

Grab bluetooth packets from an ubertooth, drop into scapy and do something...

mkfifo is SLOW! >> dont do this prior to running ubettooth-btle:
    mkfifo /tmp/bluesPipe

ubertooth-btle -f -q /mnt/usb_storage/bluesPipe
"""

import argparse
import netaddr
import re
import time
import signal
import sqlite3 as lite
import sys
import psycopg2
from scapy.all import *

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
                print(tStamp,tMac,pSignal,pNoise)

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

    ## Connect to the db
    if args.sqlite is True:
        con, db, dbName = sqlitePrep()
        PRN = sqliteFilter(db, dbName)
    else:
        con, db, dbName = pgsqlPrep()
        PRN = pgsqlFilter(db, dbName)
    p = sniff(offline = '/mnt/usb_storage/bluesPipe', prn = PRN)
    con.commit()
    con.close()


if __name__ == '__main__':
    ## ARGUMENT PARSING
    parser = argparse.ArgumentParser(description = 'airpwn-ng - the new and improved 802.11 packet injector')
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
