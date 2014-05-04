import BlockEngine
from datetime import datetime

class ClientSession(object):
    
    def __init__(self, N, g, T):
        self.clientKeyN = N
        self.clientKeyG = g
        self.T = T
        self.challenge=None
        self.blocks = None
        self.blkLocalDrive=""
        self.lost=[]
    
    def storeBlocksInMemory(self, blocks):
        self.blocks = blocks
    
    def storeBlocksInDisk(self, blockCollection):
        self.blkLocalDrive="cblk"+str(datetime.now())
        self.blkLocalDrive = self.blkLocalDrive.replace(" ", "_")
        BlockEngine.writeBlockCollectionToFile(self.blkLocalDrive, blockCollection)
    
    def storeBlocksS3(self, blockCollection):
        print "S3"
        
    def addClientChallenge(self, challenge):
        self.challenge = challenge
    
    def addLostBlocks(self, lostIndeces):
        while len(self.lost) > 0:
            self.lost.pop()
            
        for index in lostIndeces:
            self.lost.append(index)
    
    def produceProof(self):
        print "produce proof"