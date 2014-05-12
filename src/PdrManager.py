from Ibf import Ibf
from multiprocessing.managers import BaseManager
from multiprocessing.managers import BaseProxy

class IbfProxy(BaseProxy):
    _exposed_=['insert', 'zero', 'getIndices', 'binPadLostIndex', 'getCells']
    
    def insert(self,block, secret, N, g, isHashProdOne):
        self._callmethod('insert', (block, secret, N, g, isHashProdOne))
    
    def zero(self, dataBitSize):
        self._callmethod('zero', (dataBitSize,))
    
    def getIndices(self, block, isIndex):
        return self._callmethod('getIndices', (block, isIndex,))
    
    def binPadLostIndex(self, lostIndex):
        return self._callmethod('binPadLostIndex', (lostIndex,))

    def cells(self):
        return self._callmethod('getCells', ())
    

class IbfManager(BaseManager):
    pass

IbfManager.register('Ibf', Ibf, proxytype=IbfProxy,)        