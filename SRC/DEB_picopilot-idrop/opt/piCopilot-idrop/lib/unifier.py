import os
import netaddr
import packetEssentials as PE
import re
import time
from lib.location import Location

"""
server 127.127.28.0 minpoll 3 maxpoll 3
fudge 127.127.28.0 time1 .15 flag1 1 refid GPS
"""

class Unify(object):
    """This class acts a singular point of contact for tracking purposes"""

    def __init__(self, args, control = None, kBlue = None):
        self.epoch = None
        self.coord = None
        self.loc = Location()

        ## Verify GPS if enabled

        ## Set the orig timestamp
        self.origTime = int(time.time())
        self.timeMarker = self.origTime

        ## make args avail
        self.args = args

        ## idrop only
        if kBlue is None:

            ## Grab the OS control object
            self.control = control
            if args.m != 'ids':
                ## Set the driver
                self.iwDriver = self.args.d

                ## Notate driver offset
                self.PE = PE
                self.offset = self.PE.drv.drivers(self.iwDriver)

        ## Setup base
        self.baseDir = os.getcwd()

        # Grab OUIs
        print ('Loading OUIs')
        self.ouiDict = {}
        with open(self.baseDir + '/lib/support/oui.txt', 'r') as iFile:
            ouiRows = iFile.read().splitlines()
        for i in ouiRows:
            oui = re.findall('(.*)\s+\(hex\)\s+(.*)', i)
            if len(oui) == 1:
                self.ouiDict.update({oui[0][0].replace('-', ':').lower().strip(): oui[0][1]})
        print ('OUIs loaded\n')

        ## Set whitelist
        self.wSet = set()


    def macGrab(self, addr):
        """Last ditch effort if outDict{} does not have the OUI"""
        try:
            parsed_oui = netaddr.EUI(addr)
            return parsed_oui.oui.registration().org
        except netaddr.core.NotRegisteredError:
            return None


    def times(self):
        """Timestamp function

        Sets a unified timestamp marker
        """
        ### This converts to Wireshark style
        #int(wepCrypto.endSwap('0x' + p.byteRip(f.notdecoded[8:], qty = 8, compress = True)), 16)

        self.coord = self.loc.getCoord()
        self.epoch = int(time.time())                                                     ## Store the epoch in UTC
        self.pi_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.epoch))   ## Store the sql timestamp for UTC
        self.origStamp = self.origTime
        self.timeMarker = self.epoch
