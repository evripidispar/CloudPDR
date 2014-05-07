from time import time

class ExpTimer(object):
    
    def __init__(self):
        self.timers = {}
    
    def registerSession(self, session):
        self.timers[session] = {}
    
    def registerTimer(self, session, timerId):
        self.timers[session][timerId] = 0
    
    def startTimer(self, session, timerId):
        self.timers[session][timerId] = time()
    
    def endTimer(self, session, timerId):
        tEnd=time()
        self.timers[session][timerId] = tEnd - self.timers[session][timerId]