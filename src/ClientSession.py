import BlockEngine as BE
import MessageUtil as MU
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
from PdrManager import IbfManager, QSetManager
from ExpTimer import ExpTimer

def proofWorkerTask(inputQueue, blkPbSz, blkDatSz, chlng, lost, T, lock, cVal, N, ibf, g, qSets, TT):
    
    pName = mp.current_process().name
    x = ExpTimer()
    x.registerSession(pName)
    x.registerTimer(pName, "qSet")
    x.registerTimer(pName, "cSumKept")
    x.registerTimer(pName, "cTagKept")
    x.registerTimer(pName, "ibf")
    
    
    while True:
        item = inputQueue.get()
        if item == "END":
            TT[pName+str("_qSet")] = x.getTotalTimer(pName, "qSet")
            TT[pName+str("_cSumKept")] = x.getTotalTimer(pName, "cTagKept") - x.getTotalTimer(pName, "ibf")
            TT[pName+str("_cTagKept")] = x.getTotalTimer(pName, "cTagKept") - x.getTotalTimer(pName, "ibf")
            TT[pName+str("_ibf")] = x.getTotalTimer(pName, "ibf")
            
            return
        for blockPbItem in BE.chunks(item,blkPbSz):
            block = BE.BlockDisk2Block(blockPbItem, blkDatSz)
            bIndex = block.getDecimalIndex()
            if bIndex in lost:
                x.startTimer(pName, "qSet")
                binBlockIndex = block.getStringIndex()
                indices = ibf.getIndices(binBlockIndex, True)
                for i in indices:
                    with lock:
                        qSets.addValue(i, bIndex)
                
                x.endTimer(pName, "qSet")    
                del block
                continue
            x.startTimer(pName, "cSumKept")
            x.startTimer(pName, "cTakKept")
            aI = pickPseudoRandomTheta(chlng, block.getStringIndex())
            aI = number.bytes_to_long(aI)
            bI = number.bytes_to_long(block.data.tobytes())
            
            x.startTimer(pName, "ibf")
            ibf.insert(block, chlng, N, g, True)
            x.endTimer(pName, "ibf")
            
            del block
            with lock:
                cVal["cSum"] += (aI*bI)
                x.endTimer(pName,"cSumKept")
                cVal["cTag"] *= pow(T[bIndex], aI, N)
                cVal["cTag"] = pow(cVal["cTag"],1,N)
                x.endTimer(pName,"cTagKept")
                
                


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
    
    
    def produceProof(self, serverTimer, cltId):
        
        pName = mp.current_process().name
        et = ExpTimer()
        et.registerSession(pName)
        et.registerTimer(pName, "cmbLost")
        
        fp = open(self.filesystem, "rb")
        fsSize = fp.read(4)
        fsSize,  = struct.unpack("i", fsSize)
        fsMsg = CloudPdrMessages_pb2.Filesystem()
        fsMsg.ParseFromString(fp.read(int(fsSize)))
        
        ibfLength =  floor(log(fsMsg.numBlk,2)) 
        ibfLength *= (self.k+1)
        ibfLength = int(ibfLength)

        totalBlockBytes = fsMsg.numBlk * fsMsg.pbSize
        bytesPerWorker = (self.BLOCKS_PER_WORKER*totalBlockBytes) / fsMsg.numBlk
                
        gManager = mp.Manager()
        pdrManager = IbfManager()
        qSetManager = QSetManager()
        blockBytesQueue = mp.Queue(self.WORKERS)
        TT = gManager.dict()
        combinedLock = mp.Lock()
        combinedValues = gManager.dict()
        combinedValues["cSum"] = 0L
        combinedValues["cTag"] = 1L
        
        
        pdrManager.start()
        qSetManager.start()
        
        ibf = pdrManager.Ibf(self.k, ibfLength)
        print fsMsg.datSize
        ibf.zero(fsMsg.datSize)
        
        qSets = qSetManager.QSet()
        
        workerPool = []
        for i in xrange(self.WORKERS):
            p = mp.Process(target=proofWorkerTask,
                           args=(blockBytesQueue, fsMsg.pbSize, 
                                 fsMsg.datSize, self.challenge, self.lost,
                                 self.T, combinedLock, 
                                 combinedValues, self.clientKeyN, 
                                 ibf, self.clientKeyG, qSets,TT))
                           
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
        
        #print "combinedTag", combinedValues["cTag"]
        #print "combinedSum", combinedValues["cSum"]
     
        qS = qSets.qSets()
        et.startTimer(pName, "cmbLost")
        combinedLostTags = {}
        for k in qS.keys():
            print "Position:",  k
            val = qS[k]
            
            if k not in combinedLostTags.keys():
                combinedLostTags[k] = 1
                 
            for v in val:
                print "Indices in Qset", v
                binV  = ibf.binPadLostIndex(v)
                aBlk = pickPseudoRandomTheta(self.challenge, binV)
                aI = number.bytes_to_long(aBlk)
                lostTag=pow(self.T[v], aI, self.clientKeyN)
                combinedLostTags[k] = pow((combinedLostTags[k]*lostTag), 1, self.clientKeyN)
    

        et.endTimer(pName, "cmbLost")
        ibfCells = ibf.cells()
        proofMsg = MU.constructProofMessage(combinedValues["cSum"],
                                            combinedValues["cTag"],
                                            ibfCells, 
                                            self.lost ,
                                            combinedLostTags)
         
        return proofMsg
