import gpsd

class Location(object):
    
    def __init__(self):
        self.trigger = None
        try:
            gpsd.connect()
            self.gpsObj = gpsd
            self.trigger = True
        except:
            pass


    def getCoord(self):
        lCheck = None
        try:
            x = self.gpsObj.get_current()
            return x.position()
        except:
            return None
