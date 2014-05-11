
import multiprocessing as mp

class SharedCounter(object):

    def __init__(self):
        self.val = mp.Value('i', 0)
        self.lock = mp.Lock()
    
    def increment(self):
        with self.lock:
            self.val.value+=1
            print self.val.value
    
    def decrement(self):
        with self.lock:
            self.val.value-=1
    
    def getValue(self):
        with self.lock:
            return self.val.value
    
    def setValue(self, val):
        with self.lock:
            self.val.value = val
            
    def decrementIfNotZeor(self):
        with self.lock:
            if self.val.value < 0:
                self.val.value+=1
            else:
                self.val.value-=1
    
    def isPure(self):
        with self.lock:
            return self.val.value == 1
    
    def isEmpty(self):
        with self.lock:
            return self.val.value == 0