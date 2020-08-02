#!/usr/bin/python2.7

import argparse
import csv
import logging
import os
import psycopg2
import signal
import sys
from easyThread import Backgrounder
from lib.dbControl import Builder
from lib.scout import Scout
from lib.unifier import Unify
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

## Connects
cStr = "dbname='idrop' user='root' host='127.0.0.1' password='idrop'"
con = psycopg2.connect(cStr)
con.autocommit = True
db = con.cursor()

## Tables
db.execute("""
           CREATE TEMPORARY TABLE requests AS
           SELECT date, addr2, essid
           FROM probes WHERE
           subtype = 'Probe request';
           """)
db.execute("""
           CREATE TEMPORARY TABLE responses AS
           SELECT date, essid, addr2, addr1
           FROM probes WHERE
           subtype = 'Probe response';
           """)
db.execute("""
          CREATE TEMPORARY TABLE fromds AS
          SELECT date, addr3, addr1
          FROM main WHERE type = 'Data'
          AND direc = 'from-ds';
          """)
db.execute("""
          CREATE TEMPORARY TABLE tods AS
          SELECT date, addr2, addr3
          FROM main WHERE type = 'Data'
          AND direc = 'to-ds';
          """)


## Pipe logics
db.execute("""
           CREATE TEMPORARY TABLE fd AS
           SELECT date, addr1, addr3
           FROM main WHERE type = 'Data'
           AND direc = 'from-ds';
           """)
db.execute("""
           SELECT * FROM fd;
           """)
fromRows = set(db.fetchall())
db.execute("""
           SELECT * FROM tods;
           """)
toRows = set(db.fetchall())
pipeList = list(fromRows & toRows)

## fsprep
os.system('rm -f /opt/piCopilot-idrop/logs/requests.csv')
os.system('rm -f /opt/piCopilot-idrop/logs/responses.csv')
os.system('rm -f /opt/piCopilot-idrop/logs/from-ds.csv')
os.system('rm -f /opt/piCopilot-idrop/logs/to-ds.csv')
os.system('rm -f /opt/piCopilot-idrop/logs/pipes.csv')

## Outputs
db.execute("""
           copy requests to '/opt/piCopilot-idrop/logs/requests.csv' csv header;
           """)
db.execute("""
           copy responses to '/opt/piCopilot-idrop/logs/responses.csv' csv header;
           """)
db.execute("""
           copy fromds to '/opt/piCopilot-idrop/logs/from-ds.csv' csv header;
           """)
db.execute("""
           copy tods to '/opt/piCopilot-idrop/logs/to-ds.csv' csv header;
           """)
hdrs = ['date', 'x', 'y']
with open('/opt/piCopilot-idrop/logs/pipes.csv', 'w') as oFile:
    csv_out = csv.writer(oFile,
                         delimiter = ',',
                         quotechar = '"',
                         quoting = csv.QUOTE_MINIMAL)
    csv_out.writerow(hdrs)
    for row in pipeList:
        csv_out.writerow(row)
