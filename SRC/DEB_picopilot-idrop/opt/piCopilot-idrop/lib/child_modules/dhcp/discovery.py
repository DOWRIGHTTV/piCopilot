from lib.child_modules.dhcp import dicts
from scapy.all import *

dParser = dicts.Dicts()

class Discovery(object):
    """Adds DHCP Discovery entries"""
    def __init__(self, dbInstance, unity):
        self.cap = dbInstance
        self.unity = unity


    def entry(self, packet):
        """packet.haslayer('DHCP') and packet[DHCP].options[0][1] == 1"""
        pDict = {}
        for i in packet[DHCP].options:
            if type(i) is tuple:
                pDict.update({i[0]: i[1]})

        ## Insert
        self.cap.db.execute("""
                            INSERT INTO dhcp (pi_timestamp,
                                              coord,
                                              addr1,
                                              addr2,
                                              addr3,
                                              message_type,
                                              requested_addr,
                                              server,
                                              vendor,
                                              hostname)
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
                            """, (self.unity.pi_timestamp,
                                  self.unity.coord,
                                  packet.addr1,
                                  packet.addr2,
                                  packet.addr3,
                                  dParser.dhcpType(pDict.get('message-type')),
                                  pDict.get('requested_addr'),
                                  pDict.get('server_id'),
                                  pDict.get('vendor'),
                                  pDict.get('hostname')))
