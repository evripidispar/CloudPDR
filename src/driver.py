import argparse
import sys
from BlockUtil import *
from Ibf import *
#from CloudPDRObj import *
import CloudPdrFuncs
import BlockEngine as BE
from CloudPDRKey import CloudPDRKey
from TagGenerator import TagGenerator
from Crypto.Hash import SHA256
from datetime import datetime
import MessageUtil as MU
import CloudPdrMessages_pb2
from client import RpcPdrClient
from PdrSession import PdrSession
from math import floor
from math import log
from CryptoUtil import pickPseudoRandomTheta
from Crypto.Util import number
from ExpTimer import ExpTimer
import multiprocessing as mp
from TagGenerator import singleTag
from TagGenerator import singleW
import struct
from PdrManager import IbfManager, QSetManager
import copy



LOST_BLOCKS = 6

W = {}
Tags = {}

def produceClientId():
    h = SHA256.new()
    h.update(str(datetime.now()))
    return h.hexdigest()




def subsetAndLessThanDelta(clientMaxBlockId, serverLost, delta):
    
    lossLen = len(serverLost)
    if lossLen >= clientMaxBlockId:
        return (False, "Fail#1: LostSet from the server is not subset of the client blocks ")
    
    for i in serverLost:
        if i>= 0 and i <= clientMaxBlockId:
            continue
    if lossLen > delta:
        return (False, "FAIL#2: Server has lost more than DELTA blocks")
    return (True, "")


def workerTask(inputQueue,W,T,ibf,blockProtoBufSz,blockDataSz,secret,public):
    while True:
        item = inputQueue.get()
        if item == "END":
            return
        
        for blockPBItem in BE.chunks(item, blockProtoBufSz):
            block = BE.BlockDisk2Block(blockPBItem, blockDataSz)
            bIndex = block.getDecimalIndex()
#            print mp.current_process(), "Processing block", bIndex
            w = singleW(block, secret["u"])
            tag = singleTag(w, block, public["g"], secret["d"], public["n"])
            W[bIndex] = w
            T[bIndex] = tag
            ibf.insert(block, None, public["n"], public["g"], True)
            del block




def clientWorkerProof(inputQueue, blockProtoBufSz, blockDataSz, lost, chlng, W, N, comb, lock, qSets, ibf, manager):
    while True:
        item = inputQueue.get()
        if item == "END":
            return
        
        for blockPBItem in BE.chunks(item, blockProtoBufSz):
            block = BE.BlockDisk2Block(blockPBItem, blockDataSz)
            bIndex = block.getDecimalIndex()
            if bIndex in lost:
                binBlockIndex = block.getStringIndex()
                indices = ibf.getIndices(binBlockIndex, True)
                for i in indices:
                    with lock:
                        qSets.addValue(i, bIndex)
                        

                del block
                continue
            
            aI = pickPseudoRandomTheta(chlng, block.getStringIndex())
            aI = number.bytes_to_long(aI)
            h = SHA256.new()
            wI = W[bIndex]
            h.update(wI)
            wI = number.bytes_to_long(h.digest())
            wI = pow(wI, aI, N)
            with lock:
                comb["w"] *= wI
                comb["w"] = pow(comb["w"], 1, N)
            del block

        

def processServerProof(cpdrProofMsg, session, cltTimer):
    serverLost =  set()
    
    if cltTimer != None:
        cltTimer.startTimer(session.cltId, "ProcProof-Clt-SubSet")
    
    
    if len(cpdrProofMsg.proof.lostIndeces) > 0:
        res, reason = subsetAndLessThanDelta(session.fsInfo["blockNum"],
                                             cpdrProofMsg.proof.lostIndeces,
                                             session.delta)
        if res == False:
            print reason
            return False
     
    if cltTimer != None:
        cltTimer.endTimer(session.cltId, "ProcProof-Clt-SubSet")
    
    
    if cltTimer != None: 
        cltTimer.startTimer(session.cltId, "ProcProof-Clt-Te")    
    
    servLost = cpdrProofMsg.proof.lostIndeces
    serCombinedSum = long(cpdrProofMsg.proof.combinedSum)
    gS = pow(session.g, serCombinedSum, session.sesKey.key.n)
    serCombinedTag = long(cpdrProofMsg.proof.combinedTag)
    sesSecret = session.sesKey.getSecretKeyFields() 
    Te =pow(serCombinedTag, sesSecret["e"], session.sesKey.key.n)
    
#     inputQueue, blockProtoBufSz, blockDataSz, lost, chlng, W, N, combW, lock
    
    gManager = mp.Manager()
    combRes = gManager.dict()
    combRes["w"] = 1
    
    qSetManager = QSetManager()
    qSetManager.start()
    qSets = qSetManager.QSet()
    
    combLock = mp.Lock()
    bytesPerWorker = mp.Queue(session.fsInfo["workers"])
    
    workerPool = []
    for i in xrange(session.fsInfo["workers"]):
        p = mp.Process(target=clientWorkerProof,
                       args=(bytesPerWorker, session.fsInfo["pbSize"],
                             session.fsInfo["blkSz"], servLost, 
                             session.challenge, session.W, session.sesKey.key.n,
                             combRes, combLock, qSets, session.ibf, gManager))
        p.start()
        workerPool.append(p)
    
    fp = open(session.fsInfo["fsName"], "rb")
    fp.read(4)
    fp.read(session.fsInfo["skip"])
    
    while True:
        chunk = fp.read(session.fsInfo["bytesPerWorker"])
        if chunk:
            bytesPerWorker.put(chunk)
        else:
            for j in xrange(session.fsInfo["workers"]):
                bytesPerWorker.put("END")
            break
    
    for p in workerPool:
        p.join()
    
 
    combinedWInv = number.inverse(combRes["w"], session.sesKey.key.n)  #TODO: Not sure this is true
    RatioCheck1=Te*combinedWInv
    RatioCheck1 = pow(RatioCheck1, 1, session.sesKey.key.n)
    if cltTimer != None:
        cltTimer.endTimer(session.cltId, "ProcProof-Clt-Te")
         
    if RatioCheck1 != gS:
        print "FAIL#3: The Proof did not pass the first check to go to recover"
        return False

    print "# # # # # # # ##  # # # # # # # # # # # # # ##"
    
    if cltTimer != None:
        cltTimer.startTimer(session.cltId, "ProcProof-Clt-LostSum")
    qS = qSets.qSets()
    
    lostSum = {}
    for p in cpdrProofMsg.proof.lostTags.pairs:
        lostCombinedTag = long(p.v)
        Lre =pow(lostCombinedTag, sesSecret["e"], session.sesKey.key.n)
        
        Qi = qS[p.k]
        combinedWL = 1
        for vQi in Qi:
            h = SHA256.new()
            aLBlk = pickPseudoRandomTheta(session.challenge, session.ibf.binPadLostIndex(vQi))
            aLI = number.bytes_to_long(aLBlk)
            wL = session.W[vQi]
            h.update(str(wL))
            wLHash = number.bytes_to_long(h.digest())
            waL = pow(wLHash, aLI, session.sesKey.key.n)
            combinedWL = pow((combinedWL*waL), 1, session.sesKey.key.n)
        
        combinedWLInv = number.inverse(combinedWL, session.sesKey.key.n)
        lostSum[p.k] = Lre*combinedWLInv
        lostSum[p.k] = pow(lostSum[p.k], 1, session.sesKey.key.n)
    
    
    
    if cltTimer != None:
        cltTimer.endTimer(session.cltId, "ProcProof-Clt-LostSum")
       
    if cltTimer != None:
        cltTimer.startTimer(session.cltId, "ProcProof-CreateIbf-From-ProtoBuf") 
    serverStateIbf = session.ibf.generateIbfFromProtobuf(cpdrProofMsg.proof.serverState,
                                                 session.fsInfo["blkSz"])
    if cltTimer != None:
        cltTimer.endTimer(session.cltId, "ProcProof-CreateIbf-From-ProtoBuf")

    
    if cltTimer != None:
        cltTimer.startTimer(session.cltId, "ProcProof-SubtractIbf")
        
    localIbf = Ibf(session.fsInfo["k"], session.fsInfo["ibfLength"])
    
    lc = copy.deepcopy(session.ibf.cells())
    localIbf.setCells(lc)
    
#     serverIbf = Ibf(session.fsInfo["k"], session.fsInfo["ibfLength"])
#     sc  = copy.deepcopy(serverStateIbf.cells())
#     serverIbf.setCells(sc)
    
#     diffIbf = session.ibf.subtractIbf(serverStateIbf, session.challenge,
#                                      session.sesKey.key.n, session.dataBitSize, True)
    diffIbf = localIbf.subtractIbf(serverStateIbf, session.challenge,
                                    session.sesKey.key.n, session.fsInfo["blkSz"], True)
    
    if cltTimer != None:
        cltTimer.endTimer(session.cltId, "ProcProof-SubtractIbf")
    
    for k in lostSum.keys():
        val=lostSum[k]
        diffIbf.cells[k].setHashProd(val)
   
    
    if cltTimer != None:
        cltTimer.startTimer(session.cltId, "ProcProof-Recover")
    L=CloudPdrFuncs.recover(diffIbf, serverLost, session.challenge, session.sesKey.key.n, session.g)
    
    if cltTimer != None:
        cltTimer.endTimer(session.cltId, "ProcProof-Recover")
    
    for k in lostSum.keys():
        print diffIbf.cells[k].hashProd
        
    if L==None:
        print "fail to recover"
        sys.exit(1)
        
    for blk in L:
        print blk.getDecimalIndex()
      
    return "Exiting Recovery..."

def processClientMessages(incoming, session, cltTimer, lostNum=None):
    
    cpdrMsg = MU.constructCloudPdrMessageNet(incoming)
    
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT_ACK:
        print "Processing INIT-ACK"
        if cltTimer!=None:
            cltTimer.startTimer(session.cltId, "LossMessage-Create")
        lostMsg = MU.constructLossMessage(lostNum, session.cltId)
        if cltTimer != None:
            cltTimer.endTimer(session.cltId, "LossMessage-Create")
        return lostMsg
        
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.LOSS_ACK:
        print "Processing LOSS_ACK"
        
        if cltTimer != None:
            cltTimer.startTimer(session.cltId, "ChallengeMsg-Create")
        session.challenge = session.sesKey.generateChallenge()
        challengeMsg = MU.constructChallengeMessage(session.challenge, session.cltId)
        if cltTimer != None:
            cltTimer.endTimer(session.cltId, "ChallengeMsg-Create")
        return challengeMsg    
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.PROOF:
        print "Received Proof"
        res = processServerProof(cpdrMsg, session, cltTimer)
        print res




def main():
    
    p = argparse.ArgumentParser(description='Driver for IBF')

    
    p.add_argument('-b', dest='blkFp', action='store', default=None,
                   help='Serialized block filename as generated from BlockEngine')
    
    p.add_argument('-k', dest='hashNum', action='store', type=int,
                   default=5, help='Number of hash arguments')
    
    p.add_argument('-g', dest="genFile", action="store", default=None,
                 help="static generator file")
    
    p.add_argument('-n', dest='n', action='store', type=int,
                   default=1024, help='RSA modulus size')
    
    p.add_argument('-s', dest='size', action='store', type=int, default=512,
                   help='Data Bit Size')
    
    p.add_argument('-l', dest='lostNum', action='store', type=int, default=5,
                   help='Number of Lost Packets')
    
    p.add_argument('--task', dest='task', action='store', type=int, default=100,
                   help='Number of blocks per worker for the W,Tag calculation')
   
    p.add_argument('-w', dest="workers", action='store', type=int, default=4,
                  help='Number of worker processes ')

    args = p.parse_args()
    if args.hashNum > 10: 
        print "Number of hashFunctions should be less than 10"
        sys.exit(1)
        
    if args.blkFp == None:
        print 'Please specify a file that stores the block collection'
        sys.exit(1)
    
    if args.genFile == None:
        print 'Please specify a generator file'
        sys.exit(1)
        
    #Generate client id
    cltId = produceClientId()
       
   
    #Create current session
    pdrSes = PdrSession(cltId)
    
    
    
    
    #Read the generator from File
    fp = open(args.genFile, "r")
    g = fp.read()
    g = long(g)
    fp.close() 
    pdrSes.addG(g)
    
    #Generate key class
    pdrSes.sesKey = CloudPDRKey(args.n, g)
    secret = pdrSes.sesKey.getSecretKeyFields()
    public = pdrSes.sesKey.getPublicKeyFields()
    pdrSes.addSecret(secret)
    pubPB = pdrSes.sesKey.getProtoBufPubKey()
    
    
    fp=open(args.blkFp,"rb")
    fsSize = fp.read(4)
    fsSize, = struct.unpack("i", fsSize)
    fs = CloudPdrMessages_pb2.Filesystem()
    fs.ParseFromString(fp.read(int(fsSize)))
    
    ibfLength =  floor(log(fs.numBlk,2)) 
    ibfLength *= (args.hashNum+1)
    ibfLength = int(ibfLength)
    pdrSes.addibfLength (ibfLength)
    
    
    
    #fs, fsFp = BlockEngine.getFsDetailsStream(args.blkFp)
    totalBlockBytes = fs.pbSize*fs.numBlk
    bytesPerWorker = (args.task*totalBlockBytes)/ fs.numBlk
    
    pdrSes.addFsInfo(fs.numBlk, fs.pbSize, fs.datSize, int(fsSize), 
                     bytesPerWorker, args.workers, args.blkFp, ibfLength, args.hashNum)
    
    genericManager = mp.Manager()
    pdrManager = IbfManager()
    
    blockByteChunks = genericManager.Queue(args.workers)
    W = genericManager.dict()
    T = genericManager.dict()
    
    pdrManager.start()
    ibf = pdrManager.Ibf(args.hashNum, ibfLength)
    ibf.zero(fs.datSize)
    
    
    pool = []
    for i in xrange(args.workers):
        p = mp.Process(target=workerTask, args=(blockByteChunks,W,T,ibf,fs.pbSize,fs.datSize,secret,public))
        p.start()
        pool.append(p)
    
    while True:
        chunk = fp.read(bytesPerWorker)
        if chunk:
            blockByteChunks.put(chunk)
        else:
            for j in xrange(args.workers):
                blockByteChunks.put("END")
            break
    
    for p in pool:
        p.join()
    
    pdrSes.addState(ibf)
    pdrSes.W = W
    log2Blocks = log(fs.numBlk, 2)
    log2Blocks = floor(log2Blocks)
    delta = int(log2Blocks)
    pdrSes.addDelta(delta)



    initMsg = MU.constructInitMessage(pubPB, args.blkFp,
                                               T, cltId, args.hashNum, delta, fs.numBlk)

    clt = RpcPdrClient()    
    print "Sending Initialization message"
    initAck = clt.rpc("127.0.0.1", 9090, initMsg) 
    print "Received Initialization ACK"
    
    
    lostMsg = processClientMessages(initAck, pdrSes, None, args.lostNum)
    print "Sending Lost message"
    lostAck = clt.rpc("127.0.0.1", 9090, lostMsg)
    print "Received Lost-Ack message"
    
    
    challengeMsg = processClientMessages(lostAck, pdrSes, None)
    print "Sending Challenge message"
    proofMsg = clt.rpc("127.0.0.1", 9090, challengeMsg)
    print "Received Proof message"
    processClientMessages(proofMsg, pdrSes, None)
    
#cltTimer.startTimer(cltId, "Init-Create")
#    cltTimer.endTimer(cltId, "Init-Create")
#     cltTimer.startTimer(cltId, "Init-InitAck-RTT")
    
#     cltTimer.endTimer(cltId, "Init-InitAck-RTT")
     
      
    
#     
#     
#     #Register client timers
#     cltTimer = ExpTimer()
#     cltTimer.registerSession(cltId)
#     cltTimer.registerTimer(cltId, "W-Time")
#     cltTimer.registerTimer(cltId, "Tag-Time")
#     cltTimer.registerTimer(cltId, "Pop-Clt-Ibf")
#     cltTimer.registerTimer(cltId, "Init-Create")
#     cltTimer.registerTimer(cltId, "Init-InitAck-RTT")
#     cltTimer.registerTimer(cltId, "LossMessage-Create")
#     cltTimer.registerTimer(cltId, "ChallengeMsg-Create")
#     cltTimer.registerTimer(cltId, "ProcProof-Clt-SubSet")
#     cltTimer.registerTimer(cltId, "ProcProof-Clt-Te")
#     cltTimer.registerTimer(cltId, "ProcProof-Clt-LostSum")
#     cltTimer.registerTimer(cltId, "ProcProof-CreateIbf-From-ProtoBuf")
#     cltTimer.registerTimer(cltId, "ProcProof-Recover")
#     cltTimer.registerTimer(cltId, "ProcProof-SubtractIbf")
#     cltTimer.registerTimer(cltId, "Loss-LossAck-RTT")
#     cltTimer.registerTimer(cltId, "Challenge-Proof-RTT")
#     
#     
#     #Create Wi
#     cltTimer.startTimer(cltId,"W-Time")
#     cltTimer.endTimer(cltId, "W-Time")
#     
#     
#     #Create Tags
#     cltTimer.startTimer(cltId, "Tag-Time")
#     cltTimer.endTimer(cltId, "Tag-Time")
#     tagCollection = tGen.createTagProtoBuf(T)
#    
#  
#     cltTimer.printTimer(cltId, "W-Time")  
#     cltTimer.printTimer(cltId, "Tag-Time")
#  
#  
#     #Create the local state
# 
#     #Construct InitMsg
#     
#     
#     
#     
#     
#     
#     
#     print "Sending Lost message"
#     cltTimer.startTimer(cltId, "Loss-LossAck-RTT")
#     incoming = clt.rpc("127.0.0.1", 9090, outgoing)
#     cltTimer.endTimer(cltId, "Loss-LossAck-RTT")
#     
#     
#     
#     print "Sending Challenge ...."
#     cltTimer.startTimer(cltId, "Challenge-Proof-RTT")
#     incoming = clt.rpc("127.0.0.1", 9090, outgoing)
#     cltTimer.endTimer(cltId, "Challenge-Proof-RTT")
#     
#     
# 
#     cltTimer.printSessionTimers(cltId)



if __name__ == "__main__":
    main()