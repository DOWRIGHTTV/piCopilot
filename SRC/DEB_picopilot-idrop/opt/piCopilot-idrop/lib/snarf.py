import logging
import time
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from lib.parent_modules.dhcp import Dhcp
from lib.parent_modules.probes import Probes
from lib.main import Main
from lib.notifier import Alert
from lib.shared import Shared

class Snarf(object):
    """Main class for packet handling"""
    def __init__(self, dbInstance, unity, sProtocol):
        if unity.args.z is True:
            print ('snarf.Snarf instantiated')

        self.cap = dbInstance
        self.unity = unity
        self.main = Main(self.cap, self.unity)
        self.protocols = []
        self.unity.seenDict = {}
        self.packetCount = 0
        self.alt = Alert()
        self.kSeen = None

        ### Eventually backport this
        self.sh = Shared()

        print ('Using pkt silent time of:\n{0}\n'.format(self.unity.seenMaxTimer))

        if sProtocol is not None:
            self.protocols = [i for i in sProtocol]
            if 'dhcp' in self.protocols:
                self.dhcp = Dhcp(self.cap, self.unity)
                #print('added dhcp')
            if 'probes' in self.protocols:
                self.probes = Probes(self.cap, self.unity)
                #print('added probes')

        ## Deal with PCAP storage
        if self.unity.args.pcap:
            tStamp = time.strftime('%Y%m%d_%H%M', time.localtime()) + '.pcap'
            pLog = self.cap.dDir + '/' + tStamp
            self.pStore = PcapWriter(pLog, sync = True)
        else:
            self.pStore = False

        ## Track unique addr combos
        if unity.args.psql is True:
            self.cap.db.execute('CREATE TABLE IF NOT EXISTS uniques(pid INT,\
                                                                    epoch INT,\
                                                                    pi_timestamp TIMESTAMPTZ,\
                                                                    date TEXT,\
                                                                    time TEXT,\
                                                                    type TEXT,\
                                                                    subtype TEXT,\
                                                                    FCfield TEXT,\
                                                                    addr1 TEXT,\
                                                                    addr2 TEXT,\
                                                                    addr3 TEXT,\
                                                                    addr4 TEXT)')

    def subParser(self, packet):
        if packet.type == 0:
            self.subType = self.unity.PE.sType.mgmtSubtype(packet.subtype)
        elif packet.type == 1:
            self.subType = self.unity.PE.sType.ctrlSubtype(packet.subtype)
        elif packet.type == 2:
            self.subType = self.unity.PE.sType.dataSubtype(packet.subtype)
        else:
            self.subType = packet.subtype

        if self.subType is None:
            return packet.subtype
        else:
            return self.subType

    def k9(self, kDict):
        def snarf(packet):
            """This function listens for a given MAC
            Currently no logic for detecting FCfield, etc.
            This functionality will be added later on

            As well, no logic for multiple tgts on a given frame,
            yet.
            """
            #print self.packetCount
            #self.packetCount += 1

            tName = None
            match = False
            while match is False:
                a1 = kDict.get(packet.addr1)
                if a1 is not None:
                    tName = a1
                    match = True
                a2 = kDict.get(packet.addr2)
                if a2 is not None:
                    tName = a2
                    match = True
                a3 = kDict.get(packet.addr3)
                if a3 is not None:
                    tName = a3
                    match = True
                a4 = kDict.get(packet.addr4)
                if a4 is not None:
                    tName = a4
                    match = True
                match = True
            if tName is not None:
                self.sh.bashReturn('echo "INITIAL mark" >> /tmp/MARK')

                print ('our kSeen is {}'.format(self.kSeen))

                ## Avoid 30 second lag on first sighting
                if self.kSeen is None:
                    self.kSeen = True
                    self.sh.bashReturn('echo "2nd INITIAL mark" >> /tmp/MARK')

                    ## Handle main
                    self.handlerMain(packet)

                    ## Notify
                    print 'SNARF!! %s traffic detected!' % tName
                    notDecoded = hexstr(str(packet.notdecoded), onlyhex=1).split(' ')
                    try:
                        fSig = -(256 - int(notDecoded[self.unity.offset + 3], 16))
                    except IndexError:
                        fSig = ''
                    print 'RSSI: %s' % fSig
                    print '\n'

                    ## Timestamp
                    self.unity.times()
                    timeDelta = self.unity.origTime - self.unity.timeMarker
                    #if timeDelta > 30:

                    ## Reset the counter
                    self.unity.origTime = int(time.time())

                    notice = 'SNARF!! {0} traffic detected!'.format(tName)

                    ### MODIFY /opt/piCopilot-idrop/lib/notifier.py
                    #self.alt.notify(notice)
                    #time.sleep(3)
                    #self.cap.entry(packet)
                else:
                    ## Handle main
                    self.handlerMain(packet)


                    ## Notify
                    print 'SNARF!! %s traffic detected!' % tName
                    notDecoded = hexstr(str(packet.notdecoded), onlyhex=1).split(' ')
                    try:
                        fSig = -(256 - int(notDecoded[self.unity.offset + 3], 16))
                    except IndexError:
                        fSig = ''
                    print 'RSSI: %s' % fSig
                    print '\n'

                    ## Timestamp
                    self.unity.times()
                    timeDelta = self.unity.timeMarker - self.unity.origTime
                    print ('our delta is {0}'.format(str(timeDelta)))
                    self.sh.bashReturn('echo "sub mark {0}" >> /tmp/MARK'.format(str(timeDelta)))
                    if timeDelta > 30:
                        self.sh.bashReturn('echo "EMAIL sub mark {0}" >> /tmp/MARK'.format(str(timeDelta)))
                        ## Reset the counter
                        self.unity.origTime = int(time.time())

                        notice = 'SNARF!! {0} traffic detected!'.format(tName)

                        ### MODIFY /opt/piCopilot-idrop/lib/notifier.py
                        # self.alt.notify(notice)
                        #time.sleep(3)
                        #self.cap.entry(packet)
            else:
                return
        return snarf


    def handlerExclusion(self, packet):
        """Handles exclusions
        Currently only designed to avoid Beacon Frames

        Eventually this needs to be moved to lfilter.
        Absolutely does not belong in prn

        Returns True if packet should be excluded
        """
        if self.unity.args.e is not None:
            if 'beacon' in self.unity.args.e:
                if packet.haslayer(Dot11Beacon):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False


    ### Move to handler.py
    def handlerMain(self, packet):
        """Handles core aspect of logging

        As main is the total, only an entry to total is needed to track main
        """
        self.unity.logUpdate('total')
        self.main.trigger(packet)

    ### Move to handler.py
    ### Break this down for a speed boost
    def handlerProtocol(self, packet):
        """Handles protocol dissection aspect of logging"""
        if 'dhcp' in self.protocols:
            if self.dhcp.trigger(packet) == True:
                self.unity.logUpdate('dhcp')
        if 'probes' in self.protocols:
            if self.probes.trigger(packet) == True:
                self.unity.logUpdate('probes')


    def reader(self):
        def snarf(packet):
            """Parse a PCAP"""

            ## Test for exclusions
            if self.handlerExclusion(packet) is False:

                ## Test for whitelisting if wanted
                if len(self.unity.wSet) > 0:
                    if self.whiteLister(self.unity.wSet, packet) is False:

                        ### THIS IS ENTRY POINT
                        if self.seenTest(packet) is False:
                            ### CLEAR HOT TO LOG

                            self.handlerMain(packet)
                            self.handlerProtocol(packet)
                            if self.pStore is not False:
                                self.pStore.write(packet)

                            ## stdouts
                            self.unity.logUpdate('iterCount')
                            if self.unity.logDict.get('iterCount') == 1000:
                                #self.cap.con.commit()
                                print 'Total packets logged: %s' % self.unity.logDict.get('total')
                                self.unity.logDict.update({'iterCount': 0})
                        else:
                            return
                    else:
                        return
                else:
                    #What if it is not wanted
                    ### THIS IS ENTRY POINT
                    if self.seenTest(packet) is False:
                        ### CLEAR HOT TO LOG

                        self.handlerMain(packet)
                        self.handlerProtocol(packet)
                        if self.pStore is not False:
                            self.pStore.write(packet)

                        ## stdouts
                        self.unity.logUpdate('iterCount')
                        if self.unity.logDict.get('iterCount') == 1000:
                            #self.cap.con.commit()
                            print 'Total packets logged: %s' % self.unity.logDict.get('total')
                            self.unity.logDict.update({'iterCount': 0})
                    else:
                        return
            else:
                return
        return snarf


    def seenTest(self, packet):
        """Gather essential identifiers for "have I seen this packet" test

        Return False to continue with this test.  "seenTest", if not seen,
        then continue

        Will return False if the delta of now and previous timestamp
        for a given frame are > self.unity.seenMaxTimer {Default 30 seconds},
        otherwise we ignore, and thus by ignoring, we do not clog up the logs

        Create a table, and store this data so we can query on the fly
            - only with psql
        """
        try:
            p = (packet[Dot11].subtype,
                 packet[Dot11].type,
                 packet[Dot11].FCfield,
                 packet[Dot11].addr1,
                 packet[Dot11].addr2,
                 packet[Dot11].addr3,
                 packet[Dot11].addr4)

            ## Figure out if this combo has been seen before
            if p not in self.unity.seenDict:
                self.unity.seenDict.update({p: (1, time.time())})
                #print ('PASS TIMER')

                ## Add if psql
                if self.unity.args.psql is True:
                    pType = self.unity.PE.conv.symString(packet[Dot11], 'type')
                    subType = self.subParser(packet)
                    fcField = self.unity.PE.conv.symString(packet[Dot11], 'FCfield')
                    try:
                        self.cap.db.execute("""
                                            INSERT INTO uniques (pid,
                                                                 epoch,
                                                                 pi_timestamp,
                                                                 date,
                                                                 time,
                                                                 type,
                                                                 subtype,
                                                                 FCfield,
                                                                 addr1,
                                                                 addr2,
                                                                 addr3,
                                                                 addr4)
                                                         VALUES (%s,
                                                                 %s,
                                                                 %s,
                                                                 %s,
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
                                                  pType,
                                                  subType,
                                                  fcField,
                                                  packet.addr1,
                                                  packet.addr2,
                                                  packet.addr3,
                                                  packet.addr4))
                    except Exception as E:
                        print (E)

                return False

            ## Has been seen, now check time
            else:
                lastTime = self.unity.seenDict.get(p)[1]
                lastCount = self.unity.seenDict.get(p)[0]
                if (time.time() - lastTime) > self.unity.seenMaxTimer:

                    ## Update delta timestamp
                    self.unity.seenDict.update({p: (lastCount + 1, time.time())})

                    ### Should pass this information along to a DB for consumption `p` analysis wise


                    #print ('PASS TIMER')
                    return False
                else:
                    #print ('FAIL TIMER')
                    return True
        except:
            pass


    def sniffer(self):
        def snarf(packet):
            """Sniff the data"""

            ## Test for exclusions
            if self.handlerExclusion(packet) is False:

                ## Test for whitelisting if wanted
                if len(self.unity.wSet) > 0:
                    if self.whiteLister(self.unity.wSet, packet) is False:
                        ### THIS IS ENTRY POINT
                        if self.seenTest(packet) is False:
                            ### CLEAR HOT TO LOG

                            self.handlerMain(packet)
                            self.handlerProtocol(packet)
                            if self.pStore is not False:
                                self.pStore.write(packet)

                            ## stdouts
                            self.unity.logUpdate('iterCount')
                            if self.unity.logDict.get('iterCount') == 1000:
                                #self.cap.con.commit()
                                print 'Total packets logged: %s' % self.unity.logDict.get('total')
                                self.unity.logDict.update({'iterCount': 0})
                        else:
                            return
                    else:
                        return
                else:
                    #What if it is not wanted
                    ### THIS IS ENTRY POINT
                    if self.seenTest(packet) is False:
                        ### CLEAR HOT TO LOG
                        self.handlerMain(packet)
                        self.handlerProtocol(packet)
                        if self.pStore is not False:
                            self.pStore.write(packet)

                        ## stdouts
                        self.unity.logUpdate('iterCount')
                        if self.unity.logDict.get('iterCount') == 1000:
                            print 'Total packets logged: %s' % self.unity.logDict.get('total')
                            self.unity.logDict.update({'iterCount': 0})
                    else:
                        return
            else:
                return
        return snarf


    def string(self, word):
        def snarf(packet):
            """This function controls what we gather and pass to the DB
            Right now, there is no filtering at all
            The object word is simply an example of closure

            The parsing work is currently done in dbControl.py,
            Eventually this needs to be a pure API type call with different libs,
            for choosing what type of db entries to make
            """
            self.cap.entry(packet)
            self.pCount += 1
            self.tCount += 1
            if self.pCount == 100:
                print '%s frames logged' % self.tCount
                self.pCount = 0
        return snarf


    def whiteLister(self, wSet, packet):
        """Return True if any addr found in wSet"""
        if packet.addr1 in wSet:
            return True
        if packet.addr2 in wSet:
            return True
        if packet.addr3 in wSet:
            return True
        if packet.addr4 in wSet:
            return True
        return False
