import gpsd


class Location:
    
    # assign class variable for imported module gpsd for compatibility with previous revision. 
    # in the future this object can potentially be referenced directly in other modules by 
    # importing within the module itself instead of referencing through the Location class.
    gpsObj = gpsd
    
    __slots__ = (
        'trigger',
    )
    
    def __init__(self):
        self.trigger = None
        try:
            gpsd.connect()
        except:
            pass
        else:
            self.trigger = True

    def getCoord(self):
        lCheck = None # NOTE: is this needed?
        try:
            return self.gpsObj.get_current().position()
        except:
            return None
