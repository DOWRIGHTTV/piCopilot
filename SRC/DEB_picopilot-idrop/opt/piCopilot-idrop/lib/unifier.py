import os
import netaddr
import packetEssentials as PE
import re
import time

class Unify(object):
    """This class acts a singular point of contact for tracking purposes"""

    def __init__(self, args, control = None, kBlue = None):
        if kBlue is None:
            if args.z:
                print ('unifier.Unify instantiated')
        self.epoch = None
        self.lDate = None
        self.lTime = None

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

            ## Packet logs
            self.logDict = {'ids': 0,
                            'iterCount': 0,
                            'dhcp': 0,
                            'probes': 0,
                            'total': 0}
        ## kBlue usage
        else:
            self.logDict = {'blue': 0}

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


    def logUpdate(self, key):
        """Increase the count by 1 for a given key"""
        count = self.logDict.get(key)
        self.logDict.update({key: count + 1})


    def times(self):
        """Timestamp function

        Sets a unified timestamp marker
        """
        ### This converts to Wireshark style
        #int(wepCrypto.endSwap('0x' + p.byteRip(f.notdecoded[8:], qty = 8, compress = True)), 16)
        self.epoch = int(time.time())                                           ## Store the epoch in UTC
        self.lDate = time.strftime('%Y-%m-%d', time.localtime(self.epoch))      ## Store the date in local tz
        self.lTime = time.strftime('%H:%M:%S', time.localtime(self.epoch))      ## Store the time in local tz
        self.origStamp = self.origTime
        self.timeMarker = self.epoch
