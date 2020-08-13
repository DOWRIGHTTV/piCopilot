import getpass
import logging
import os
import psycopg2
import sys
import time
import sqlite3 as lite
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

class Builder(object):
    """This class builds or adds on to a pre-existing sqlite3/psql database"""

    def __init__(self, unity):

        ## Unify
        self.unity = unity

        ## Create Base directory
        self.bDir = os.getcwd()

        ## Logs
        self.dDir = '%s/logs' % self.bDir
        if not os.path.isdir(self.dDir):
            os.makedirs(self.dDir)

        ## Create directory list for dDir
        self.dList = os.listdir(self.dDir)

        ## Construct and connect to the sqlite db
        if not unity.args.psql:

            ## Create DB
            tStamp = time.strftime('%Y%m%d_%H%M', time.localtime()) + '.sqlite'
            self.dbName = '%s/%s' % (self.dDir, tStamp)

            ## Check to make sure we want to continue if manual mode
            if self.unity.args.z is True:
                if os.path.isfile(self.dbName):
                    try:
                        self.dFile = raw_input('%s already exists\nUpdate and continue? [y/N]\n' % self.dbName)
                    except:
                        self.dFile = input('%s already exists\nUpdate and continue? [y/N]\n' % self.dbName)
                    if not self.dFile:
                        exit(1)
                    elif self.dFile == 'n':
                        exit(1)
                    elif self.dFile == 'N':
                        exit(1)
                    else:
                        print '\nUpdating %s and continuing' % self.dbName

            ## Build the DB if not already created
            print 'Proceeding to build %s\n' % self.dbName
            self.con = lite.connect(self.dbName, isolation_level = None)
            self.con.text_factory = str
            self.db = self.con.cursor()

        ## Construct and connect to the psql db
        else:

            if self.unity.args.m != 'ids':
                try:
                    cStr = "dbname='idrop' user='%s' host='%s' password='%s'" % (unity.args.user, unity.args.host, unity.args.password)
                    self.con = psycopg2.connect(cStr)
                    self.con.autocommit = True
                    self.db = self.con.cursor()

                    ## Test for wipe
                    if self.unity.args.wipe is True:
                        self.db.execute('DROP TABLE IF EXISTS dhcp;')
                        self.db.execute('DROP TABLE IF EXISTS main;')
                        self.db.execute('DROP TABLE IF EXISTS probes;')
                        self.db.execute('DROP TABLE IF EXISTS uniques;')
                        self.con.close()
                        print('Tables dropped\n  [+] Exiting\n')
                        sys.exit(0)
                except:
                    print ("I am unable to connect to the database idrop")
                    sys.exit(1)
            else:

                ## Postgres checks  << Move up in the logic stack
                checks = True
                if self.unity.args.host is None:
                    print('  --host is required for PGSQL usage')
                    checks = False
                if self.unity.args.user is None:
                    print('  --user is required for PGSQL usage')
                    checks = False
                if self.unity.args.fwip is None:
                    print('  --fwip is required for PGSQL usage')
                    checks = False
                if self.unity.args.id is None:
                    print('  --id is required for PGSQL usage')
                    checks = False

                if checks is False:
                    print('')
                    sys.exit(1)

                try:
                    self.pWord = getpass.getpass('PSQL Password?\n')
                    cStr = "dbname='ids' user='%s' host='%s' password='%s' sslmode='verify-full'" % (unity.args.user, unity.args.host, self.pWord)
                    self.con = psycopg2.connect(cStr)
                    self.con.autocommit = True
                    self.db = self.con.cursor()

                    ## Test for wipe
                    if self.unity.args.wipe is True:
                        self.db.execute('DROP TABLE IF EXISTS ids;')
                        self.db.execute('DROP TABLE IF EXISTS heartbeats;')
                        self.con.close()
                        print('Tables dropped\n  [+] Exiting\n')
                        sys.exit(0)
                except:
                    print ("I am unable to connect to the database ids")
                    sys.exit(1)


    def heartStamp(self):
        return time.strftime('%Y%m%d-%H%M%S', time.localtime())
