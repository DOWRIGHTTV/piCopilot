from lib.child_modules.dhcp import discovery
from lib.child_modules.dhcp import request
from scapy.all import *

class Dhcp(object):
    """Handles all aspects of DHCP for 802.11"""

    def __init__(self, dbInstance, unity):
        self.unity = unity
        self.discovery = discovery.Discovery(dbInstance, unity)
        self.request = request.Request(dbInstance, unity)

        ## Create
        dbInstance.db.execute("""
                              CREATE TABLE IF NOT EXISTS dhcp(pi_timestamp TIMESTAMPTZ,
                                                              coord TEXT,
                                                              addr1 TEXT,
                                                              addr2 TEXT,
                                                              addr3 TEXT,
                                                              message_type TEXT,
                                                              requested_addr TEXT,
                                                              server TEXT,
                                                              vendor TEXT,
                                                              hostname TEXT);
                              """)

    def trigger(self, packet):
        """Trigger mechanism for DHCP entries

        Returns True if:
            - DHCP Discovery
            - DHCP Request
        Otherwise returns False
        """

        ## DHCP Discovery
        if packet.haslayer('DHCP'):
            if packet[DHCP].options[0][1] == 1:
                self.discovery.entry(packet)
                return True

        ## DHCP Request
        elif packet.haslayer('DHCP'):
            if packet[DHCP].options[0][1] == 3:
                self.request.entry(packet)
                return True

        else:
            return False
