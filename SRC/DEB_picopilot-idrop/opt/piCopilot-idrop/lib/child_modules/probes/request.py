from scapy.all import *

class Request(object):
    """Adds Probe Request entries to a pre-existing sqlite3/psql database"""
    def __init__(self, dbInstance, unity):
        self.cap = dbInstance
        self.unity = unity


    def entry(self, packet):
        """packet.haslayer('Dot11ProbeReq')"""

        ## sqlite
        if self.unity.args.psql is not True:
            try:
                self.cap.db.execute("""
                                    INSERT INTO `probes` VALUES(?,
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?,
                                                                ?);
                                    """, (self.unity.logDict.get('total'),
                                          self.unity.epoch,
                                          str(self.unity.lDate) + ' ' + str(self.unity.lTime) + '-05',
                                          self.unity.lDate,
                                          self.unity.lTime,
                                          self.unity.PE.sType.mgmtSubtype(packet.subtype),
                                          packet.addr1,
                                          packet.addr2,
                                          str(packet[Dot11Elt].info)))
            except Exception as E:
                print (E)

        ## psql
        else:
            try:
                self.cap.db.execute("""
                                    INSERT INTO probes (pid,
                                                        epoch,
                                                        pi_timestamp,
                                                        date,
                                                        time,
                                                        subtype,
                                                        addr1,
                                                        addr2,
                                                        essid)
                                                VALUES (%s,
                                                        %s,
                                                        %s,
                                                        %s,
                                                        %s,
                                                        %s,
                                                        %s,
                                                        %s,
                                                        %s);
                                    """, (self.unity.logDict.get('total'),
                                          self.unity.epoch,
                                          str(self.unity.lDate) + ' ' + str(self.unity.lTime) + '-05',
                                          self.unity.lDate,
                                          self.unity.lTime,
                                          self.unity.PE.sType.mgmtSubtype(packet.subtype),
                                          packet.addr1,
                                          packet.addr2,
                                          str(packet[Dot11Elt].info)))
            except Exception as E:
                print (E)
