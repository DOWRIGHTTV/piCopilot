from scapy.all import *

class Main(object):
    """Handles Main logging aspect for 802.11"""

    def __init__(self, dbInstance, unity, wireless = True):
        if unity.args.z:
            print('main.Main instantiated')
        self.unity = unity
        self.cap = dbInstance

        ## popList work
        self.popDict = {}

        ## sqlite
        if self.unity.args.psql is not True:
            if wireless is True:
                self.cap.db.execute("""
                                    CREATE TABLE IF NOT EXISTS main(pid INTEGER,
                                                                    epoch INTEGER,
                                                                    pi_timestamp TIMESTAMPTZ,
                                                                    date TEXT,
                                                                    time TEXT,
                                                                    addr1_oui TEXT,
                                                                    addr1 TEXT,
                                                                    addr2_oui TEXT,
                                                                    addr2 TEXT,
                                                                    addr3_oui TEXT,
                                                                    addr3 TEXT,
                                                                    addr4_oui TEXT,
                                                                    addr4 TEXT,
                                                                    type TEXT,
                                                                    subtype TEXT,
                                                                    rssi INTEGER,
                                                                    direc TEXT,
                                                                    fcfield INTEGER,
                                                                    channel INTEGER,
                                                                    frequency INTEGER);
                                    """)

        ## pgsql
        else:
            if wireless is True:
                self.cap.db.execute("""
                                    CREATE TABLE IF NOT EXISTS main(pid INT,
                                                                    epoch INTEGER,
                                                                    pi_timestamp TIMESTAMPTZ,
                                                                    date TEXT,
                                                                    time TEXT,
                                                                    addr1_oui TEXT,
                                                                    addr1 TEXT,
                                                                    addr2_oui TEXT,
                                                                    addr2 TEXT,
                                                                    addr3_oui TEXT,
                                                                    addr3 TEXT,
                                                                    addr4_oui TEXT,
                                                                    addr4 TEXT,
                                                                    type TEXT,
                                                                    subtype TEXT,
                                                                    rssi INT,
                                                                    direc TEXT,
                                                                    fcfield INT,
                                                                    channel INT,
                                                                    frequency INT);
                                    """)


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


    def trigger(self, packet):
        """Trigger mechanism for main entries

        The overlap, while it works in RF, doesn't work on the NIC
        Some NICs see the overlap, but the headers still show the current chan
        """
        fChannel = self.unity.control.curChan
        fFreq = self.unity.control.curFreq
        fSig = packet[RadioTap].dBm_AntSignal

        ## Values for DB entry
        pType = self.unity.PE.conv.symString(packet[Dot11], 'type')
        subType = self.subParser(packet)


        ### Need to boolean this out cleaner
        fromDS = False
        toDS = False
        fcField = None
        if self.unity.PE.pt.nthBitSet(packet[Dot11].FCfield, 0) is True:
            toDS = True
        if self.unity.PE.pt.nthBitSet(packet[Dot11].FCfield, 1) is True:
            fromDS = True

        if toDS & fromDS:
            fcField = 'mesh'
        elif toDS:
            fcField = 'to-ds'
        elif fromDS:
            fcField = 'from-ds'
        ###


        ## OUI prep
        try:
            o1 = self.unity.ouiDict.get(':'.join(packet.addr1.split(':')[0:3]))
        except:
            try:
                o1 = self.unity.macGrab(packet.addr1)
            except:
                o1 = None

        try:
            o2 = self.unity.ouiDict.get(':'.join(packet.addr2.split(':')[0:3]))
        except:
            try:
                o2 = self.unity.macGrab(packet.addr2)
            except:
                o2 = None

        try:
            o3 = self.unity.ouiDict.get(':'.join(packet.addr3.split(':')[0:3]))
        except:
            try:
                o3 = self.unity.macGrab(packet.addr3)
            except:
                o3 = None

        try:
            o4 = self.unity.ouiDict.get(':'.join(packet.addr4.split(':')[0:3]))
        except:
            try:
                o4 = self.unity.macGrab(packet.addr4)
            except:
                o4 = None

        ## Mark the time
        self.unity.times()

        ## sqlite
        if self.unity.args.psql is not True:
            self.cap.db.execute("""
                                INSERT INTO main VALUES(?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
                                                        ?,
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
                                      str(self.unity.lDate) + ' ' + str(self.unity.lTime),
                                      self.unity.lDate,
                                      self.unity.lTime,
                                      o1,
                                      packet.addr1,
                                      o2,
                                      packet.addr2,
                                      o3,
                                      packet.addr3,
                                      o4,
                                      packet.addr4,
                                      pType,
                                      subType,
                                      fSig,
                                      fcField,
                                      int(packet[Dot11].FCfield),
                                      fChannel,
                                      fFreq))


        ## pgsql
        else:
            self.cap.db.execute("""
                                INSERT INTO main (pid,
                                                  epoch,
                                                  pi_timestamp,
                                                  date,
                                                  time,
                                                  addr1_oui,
                                                  addr1,
                                                  addr2_oui,
                                                  addr2,
                                                  addr3_oui,
                                                  addr3,
                                                  addr4_oui,
                                                  addr4,
                                                  type,
                                                  subtype,
                                                  rssi,
                                                  direc,
                                                  fcfield,
                                                  channel,
                                                  frequency)
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
                                      str(self.unity.lDate) + ' ' + str(self.unity.lTime),
                                      self.unity.lDate,
                                      self.unity.lTime,
                                      o1,
                                      packet.addr1,
                                      o2,
                                      packet.addr2,
                                      o3,
                                      packet.addr3,
                                      o4,
                                      packet.addr4,
                                      pType,
                                      subType,
                                      fSig,
                                      fcField,
                                      int(packet[Dot11].FCfield),
                                      fChannel,
                                      fFreq))

        return True
