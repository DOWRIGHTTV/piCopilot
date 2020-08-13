class Dicts(object):
    """DHCP Dictionaries for type conversions"""

    def dhcpType(self, val):
        """DHCP Type converter"""
        typeDict = {1: 'discover',
                    2: 'offer',
                    3: 'request',
                    4: 'decline',
                    5: 'ack',
                    6: 'nak',
                    7: 'release',
                    8: 'inform',
                    9: 'force_renew',
                    10:'lease_query',
                    11:'lease_unassigned',
                    12:'lease_unknown',
                    13:'lease_active'}
        return typeDict.get(val)
