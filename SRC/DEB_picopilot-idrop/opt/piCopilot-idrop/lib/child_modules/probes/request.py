from scapy.all import *

class Request(object):
    """Adds Probe Request entries"""
    def __init__(self, dbInstance, unity):
        self.cap = dbInstance
        self.unity = unity


    def entry(self, packet):
        """packet.haslayer('Dot11ProbeReq')"""
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
                                        self.unity.pi_timestamp,
                                        self.unity.lDate,
                                        self.unity.lTime,
                                        self.unity.PE.sType.mgmtSubtype(packet.subtype),
                                        packet.addr1,
                                        packet.addr2,
                                        packet[Dot11Elt].info.decode()))
        except Exception as E:
            print (E)
