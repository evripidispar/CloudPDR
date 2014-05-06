import BlockEngine
import MessageUtil
from datetime import datetime
from Crypto.Random import random
from CryptoUtil import pickPseudoRandomTheta
from Crypto.Util import number
from Ibf import Ibf

class ClientSession(object):
    
    BLOCK_INDEX_LEN=32
    
    def __init__(self, N, g, T, delta, k):
        self.clientKeyN = N
        self.clientKeyG = g
        self.T = T
        self.challenge=None
        self.blocks = None
        self.blkLocalDrive=""
        self.lost=[]
        self.delta = delta
        self.k = k
        
    
    def storeBlocksInMemory(self, blocks, blockBitSize):
        self.blocks = blocks
        self.ibfLength = int(self.delta *(self.k+1)) 
        self.blockBitSize = blockBitSize
    
    def storeBlocksInDisk(self, blockCollection):
        self.blkLocalDrive="cblk"+str(datetime.now())
        self.blkLocalDrive = self.blkLocalDrive.replace(" ", "_")
        BlockEngine.writeBlockCollectionToFile(self.blkLocalDrive, blockCollection)
    
    def storeBlocksS3(self, blockCollection):
        print "S3"
        
    def addClientChallenge(self, challenge):
        self.challenge = str(challenge)
    
    def addLostBlocks(self, lostIndeces):
        while len(self.lost) > 0:
            self.lost.pop()
            
        for index in lostIndeces:
            self.lost.append(index)
    
    def chooseBlocksToLose(self, lossNum):
        while len(self.lost) > 0:
            self.lost.pop()
            
        for index in random.sample(range(len(self.blocks)), lossNum):
            self.lost.append(index)
    
    
    def findCombinedValues(self):
        index = 0
        combinedSum = 0
        combinedTag = 1
        fp = open("aIserver.txt", "w")
        for blk in self.blocks:
            if index in self.lost:
                index+=1
                continue
            
            aBlk = pickPseudoRandomTheta(self.challenge, blk.getStringIndex())
            aI = number.bytes_to_long(aBlk)
            fp.write(str(aI)+"\n")
            bI = number.bytes_to_long(blk.data.tobytes())
            combinedSum += (aI*bI)
            combinedTag *= pow(self.T[index], aI, self.clientKeyN)
            combinedTag = pow(combinedTag, 1, self.clientKeyN)
            index+=1
       
        fp.close()
        return (combinedSum, combinedTag)
        
    
    def produceProof(self):
    
        combinedSum, combinedTag = self.findCombinedValues()
        ibf = Ibf(self.k, self.ibfLength)
        ibf.zero(self.blockBitSize)
        
        index=0
        for blk in self.blocks:
            if index in self.lost:
                print "Correct", self.lost, index
                index+=1
                continue
            ibf.insert(blk, self.challenge,
                        self.clientKeyN, 
                        self.clientKeyG, True)
            index+=1
    
        qSets = [[] for x in xrange(self.ibfLength)]
        for lIndex in self.lost:
            #print lIndex
            binLostIndex = ibf.binPadLostIndex(lIndex)
            indeces = ibf.getIndices(binLostIndex, True)
            
            for i in indeces:
                #print i
                #if i not in qSets.keys():
                    #qSets[i] = set()
                qSets[i].append(lIndex)
            
        #for x in xrange(self.ibfLength):
            #val=qSets[x]
            #for v in val:
                 #print v
                    
                
        
        combinedLostTags = {}
        for k in xrange(self.ibfLength):
            if  qSets[k]!=[]:
                print "Position in the Ibf", k
                val = qSets[k]
                #for v in val:
                    #print v
                if k not in combinedLostTags.keys():
                    combinedLostTags[k] = 1
                
                for v in val:
                    print "Things in qset", v
                    binV  = ibf.binPadLostIndex(v)
                    aBlk = pickPseudoRandomTheta(self.challenge, binV)
                    aI = number.bytes_to_long(aBlk)
                    lostTag=pow(self.T[v], aI, self.clientKeyN)
                    combinedLostTags[k] = pow((combinedLostTags[k]*lostTag), 1, self.clientKeyN)
                #print combinedLostTags[k]
        
        return (combinedSum, combinedTag, ibf, combinedLostTags)
