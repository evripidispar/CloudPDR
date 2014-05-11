import BlockEngine as BE
import MessageUtil
from datetime import datetime
from Crypto.Random import random
from CryptoUtil import pickPseudoRandomTheta
from Crypto.Util import number
from Ibf import Ibf
import itertools
import numpy as np
import multiprocessing as mp
from math import floor, log
import CloudPdrMessages_pb2
import struct

# 
#  index = 0
#         combinedSum = 0
#         combinedTag = 1
#         fp = open("aIserver.txt", "w")
#         for blk in self.blocks:
#             if index in self.lost:
#                 index+=1
#                 continue
#             
#             aBlk = pickPseudoRandomTheta(self.challenge, blk.getStringIndex())
#             aI = number.bytes_to_long(aBlk)
#             fp.write(str(aI)+"\n")
#             bI = number.bytes_to_long(blk.data.tobytes())
#             combinedSum += (aI*bI)
#             combinedTag *= pow(self.T[index], aI, self.clientKeyN)
#             combinedTag = pow(combinedTag, 1, self.clientKeyN)
#             index+=1
#        
#         fp.close()
#         return (combinedSum, combinedTag)



def proofWorkerTask(inputQueue, blkPbSz, blkDatSz, chlng, lost, T, lock, cSum, cTag, N):
    
    while True:
        item = inputQueue.get()
        if item == "END":
            return
        for blockPbItem in BE.chunks(item,blkPbSz):
            block = BE.BlockDisk2Block(blockPbItem, blkDatSz)
            bIndex = block.getDecimalIndex()
            if bIndex in lost:
                continue
            aI = pickPseudoRandomTheta(chlng, block.getStringIndex())
            aI = number.bytes_to_long(aI)
            bI = number.bytes_to_long(block.data.tobytes())
            tagI = pow(T[bIndex], aI, N)
            #TODO add the ibf insert
            del block
            with lock:
                cSum.value += (aI*bI)
                cTag.value *= tagI
                cTag = pow(cTag,1,N)
                
            



class ClientSession(object):
    
    WORKERS = 4
    BLOCK_INDEX_LEN=32
    BLOCKS_PER_WORKER=200
    
    def __init__(self, N, g, tagMsg, delta, k, fs, blkNum):
        self.clientKeyN = N
        self.clientKeyG = g
        self.T = {}
        self.challenge=None
        self.blocks = None
        self.blkLocalDrive=""
        self.lost=None
        self.delta = delta
        self.k = k
        self.filesystem = fs
        self.fsBlocksNum = blkNum
        self.populateTags(tagMsg)
        
    def populateTags(self, tagMsg):
        
        iters = itertools.izip(tagMsg.index,tagMsg.tags)
        for index,tag in iters:
            self.T[index]=long(tag)
        
    
    def storeBlocksInMemory(self, blocks, blockBitSize):
        self.blocks = blocks
        self.ibfLength = int(self.delta *(self.k+1)) 
        self.blockBitSize = blockBitSize
    
    def storeBlocksInDisk(self, blockCollection):
        self.blkLocalDrive="cblk"+str(datetime.now())
        self.blkLocalDrive = self.blkLocalDrive.replace(" ", "_")
        BE.writeBlockCollectionToFile(self.blkLocalDrive, blockCollection)
    
    def storeBlocksS3(self, blockCollection):
        print "S3"
        
    def addClientChallenge(self, challenge):
        self.challenge = str(challenge)
     
    def chooseBlocksToLose(self, lossNum):
        self.lost = np.random.random_integers(0, self.fsBlocksNum-1, lossNum)
    
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
        
    
    
    def produceProof(self, serverTimer, cltId):
        
        
        fp = open(self.filesystem, "rb")
        fsSize = fp.read(4)
        fsSize = struct.unpack("i", fsSize)
        fsMsg = CloudPdrMessages_pb2.Filesystem()
        
        ibfLength =  floor(log(fsMsg.numBlk,2)) 
        ibfLength *= (self.k+1)
        ibfLength = int(ibfLength)
    
        totalBlockBytes = fsMsg.numBlk * fsMsg.pbSize
        bytesPerWorker = (self.BLOCKS_PER_WORKER*totalBlockBytes) / fsMsg.numBlk
        
        
        gManager = mp.Manager()
        blockBytesQueue = mp.Queue(self.WORKERS)
        combinedSumVal = mp.Value("L", 0)
        combinedTagVal = mp.Value("L", 1)
        combinedLock = mp.Lock()
        
        workerPool = []
        for i in xrange(self.WORKERS):
            p = mp.Process(target=proofWorkerTask,
                           args=())
            p.start()
            workerPool.append(p)
        
        while True:
            chunk = fp.read(bytesPerWorker)
            if chunk:
                blockBytesQueue.put(chunk)
            else:
                for j in xrange(self.WORKERS):
                    blockBytesQueue.put("END")
                break
        
        for p in workerPool:
            p.join()
        
    
    
    
#         serverTimer.startTimer(cltId, "Server-ProofCombinedValues")
#         combinedSum, combinedTag = self.findCombinedValues()
#         serverTimer.endTimer(cltId, "Server-ProofCombinedValues")
#         ibf = Ibf(self.k, self.ibfLength)
#         ibf.zero(self.blockBitSize)
#         
#         
#         
#         index=0
#         serverTimer.startTimer(cltId, "Server-ProofIbfInsert")
#         for blk in self.blocks:
#             if index in self.lost:
#                 print "Correct", self.lost, index
#                 index+=1
#                 continue
#             ibf.insert(blk, self.challenge,
#                         self.clientKeyN, 
#                         self.clientKeyG, True)
#             index+=1
#         serverTimer.endTimer(cltId, "Server-ProofIbfInsert")
# 
# 
#         serverTimer.startTimer(cltId, "Server-ProofCombinedLostTags")
#         qSets={}
#         for lIndex in self.lost:
#             binLostIndex = ibf.binPadLostIndex(lIndex)
#             indeces = ibf.getIndices(binLostIndex, True)
#             
#             for i in indeces:
#                 if i not in qSets.keys():
#                         qSets[i] = []
#                 qSets[i].append(lIndex)
#                             
#         
#         combinedLostTags = {}
#         for k in qSets.keys():
#             print "Position:",  k
#             val = qSets[k]
#             if k not in combinedLostTags.keys():
#                 combinedLostTags[k] = 1
#                 
#             for v in val:
#                 print "Indices in Qset", v
#                 binV  = ibf.binPadLostIndex(v)
#                 aBlk = pickPseudoRandomTheta(self.challenge, binV)
#                 aI = number.bytes_to_long(aBlk)
#                 lostTag=pow(self.T[v], aI, self.clientKeyN)
#                 combinedLostTags[k] = pow((combinedLostTags[k]*lostTag), 1, self.clientKeyN)
#         serverTimer.endTimer(cltId, "Server-ProofCombinedLostTags")
#         return (combinedSum, combinedTag, ibf, combinedLostTags)
