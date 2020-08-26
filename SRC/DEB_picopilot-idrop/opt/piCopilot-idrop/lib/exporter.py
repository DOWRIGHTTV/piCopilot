import csv
import os
import psycopg2
import sys

class Exporter(object):
    """All things sql export"""

    def pgsqlConnect(self):
        ## Connects
        ### Need to fix this for config.ini purposes
        cStr = "dbname='idrop' user='root' host='127.0.0.1' password='idrop'"
        self.con = psycopg2.connect(cStr)
        self.con.autocommit = True
        self.db = self.con.cursor()


    def pgsqlExporter(self):
        ## Tables
        self.db.execute("""
                        CREATE TEMPORARY TABLE requests AS
                        SELECT date, addr2, essid
                        FROM probes WHERE
                        subtype = 'Probe request';
                        """)
        self.db.execute("""
                        CREATE TEMPORARY TABLE responses AS
                        SELECT date, essid, addr2, addr1
                        FROM probes WHERE
                        subtype = 'Probe response';
                        """)
        self.db.execute("""
                        CREATE TEMPORARY TABLE fromds AS
                        SELECT date, addr3, addr1
                        FROM main WHERE type = 'Data'
                        AND direc = 'from-ds';
                        """)
        self.db.execute("""
                        CREATE TEMPORARY TABLE tods AS
                        SELECT date, addr2, addr3
                        FROM main WHERE type = 'Data'
                        AND direc = 'to-ds';
                        """)


        ## Pipe logics
        self.db.execute("""
                        CREATE TEMPORARY TABLE fd AS
                        SELECT date, addr1, addr3
                        FROM main WHERE type = 'Data'
                        AND direc = 'from-ds';
                        """)
        self.db.execute("""
                        SELECT * FROM fd;
                        """)
        fromRows = set(self.db.fetchall())
        self.db.execute("""
                        SELECT * FROM tods;
                        """)
        toRows = set(self.db.fetchall())
        pipeList = list(fromRows & toRows)

        ## fsprep
        os.system('rm -f /opt/piCopilot-idrop/logs/requests.csv')
        os.system('rm -f /opt/piCopilot-idrop/logs/responses.csv')
        os.system('rm -f /opt/piCopilot-idrop/logs/from-ds.csv')
        os.system('rm -f /opt/piCopilot-idrop/logs/to-ds.csv')
        os.system('rm -f /opt/piCopilot-idrop/logs/pipes.csv')

        ## Outputs
        self.db.execute("""
                        copy requests to '/opt/piCopilot-idrop/logs/requests.csv' csv header;
                        """)
        self.db.execute("""
                        copy responses to '/opt/piCopilot-idrop/logs/responses.csv' csv header;
                        """)
        self.db.execute("""
                        copy fromds to '/opt/piCopilot-idrop/logs/from-ds.csv' csv header;
                        """)
        self.db.execute("""
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
