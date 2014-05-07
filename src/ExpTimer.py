from time import time

class ExpTimer(object):
    
    def __init__(self):
        self.timers = {}
    
    def registerSession(self, session):
        self.timers[session] = {}
    
    def registerTimer(self, sId, tId):
        self.timers[sId][tId] = 0
    
    def startTimer(self, sId, tId):
        self.timers[sId][tId] = time()
    
    def endTimer(self, sId, tId):
        tEnd=time()
        self.timers[sId][tId] = tEnd - self.timers[sId][tId]
    
    def printTimer(self, sId, tId):
        print tId, ":", self.timers[sId][tId] , "sec"
    
    def printSessionTimers(self, sId):
        for k in self.timers[sId].keys():
            print k, ":", self.timers[sId][k], "sec"