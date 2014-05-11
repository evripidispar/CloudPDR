import argparse
import sys
from BlockUtil import *
from Ibf import *
#from CloudPDRObj import *
import CloudPdrFuncs
import BlockEngine
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
from PdrManager import PdrManager


LOST_BLOCKS = 6

W = {}
Tags = {}

def produceClientId():
    h = SHA256.new()
    h.update(str(datetime.now()))
    return h.hexdigest()


def processServerProof(cpdrProofMsg, session, cltTimer):
    serverLost =  set()
    
    cltTimer.startTimer(session.cltId, "ProcProof-Clt-SubSet")
    if len(cpdrProofMsg.proof.lostIndeces) > 0:
        for lost in cpdrProofMsg.proof.lostIndeces:
            serverLost.add(lost)
        
        blockSet = set(range(len(session.blocks)))
        if serverLost.issubset(blockSet) == False:
            del blockSet
            print "FAIL#1: LostSet from the server is not subset of the blocks in the Client"
            return False
        
        
        if len(serverLost) > session.delta:
            print "FAIL#2: Server has lost more than DELTA blocks"
            return False
    
    cltTimer.endTimer(session.cltId, "ProcProof-Clt-SubSet")
    serCombinedSum = long(cpdrProofMsg.proof.combinedSum)
    gS = pow(session.g, serCombinedSum, session.sesKey.key.n)
    serCombinedTag = long(cpdrProofMsg.proof.combinedTag)
    sesSecret = session.sesKey.getSecretKeyFields() 
     
    cltTimer.startTimer(session.cltId, "ProcProof-Clt-Te")    
    Te =pow(serCombinedTag, sesSecret["e"], session.sesKey.key.n)
        
    index = 0
    combinedW=1
    for blk in session.blocks:
        if index in cpdrProofMsg.proof.lostIndeces:
            index+=1
            continue
        
        h = SHA256.new()
        aBlk = pickPseudoRandomTheta(session.challenge, blk.getStringIndex())
        aI = number.bytes_to_long(aBlk)
        
        w = session.W[index]
        h.update(str(w))
        wHash = number.bytes_to_long(h.digest())
        wa= pow(wHash, aI, session.sesKey.key.n)
        combinedW = pow((combinedW*wa), 1, session.sesKey.key.n)
        index+=1
            

    combinedWInv = number.inverse(combinedW, session.sesKey.key.n)  #TODO: Not sure this is true
    RatioCheck1=Te*combinedWInv
    RatioCheck1 = pow(RatioCheck1, 1, session.sesKey.key.n)
    cltTimer.endTimer(session.cltId, "ProcProof-Clt-Te")
        
    if RatioCheck1 != gS:
        print "FAIL#3: The Proof did not pass the first check to go to recover"
        return False

    print "# # # # # # # ##  # # # # # # # # # # # # # ##"
    
    
    cltTimer.startTimer(session.cltId, "ProcProof-Clt-LostSum")
    qSets = {}
    for lIndex in serverLost:
        binLostIndex = session.ibf.binPadLostIndex(lIndex)
        indeces = session.ibf.getIndices(binLostIndex, True)
            
        for i in indeces:
            if i not in qSets.keys():
                qSets[i] = []
            qSets[i].append(lIndex)
    
    
    lostSum = {}
    for p in cpdrProofMsg.proof.lostTags.pairs:
        lostCombinedTag = long(p.v)
        Lre =pow(lostCombinedTag, sesSecret["e"], session.sesKey.key.n)
        
        Qi = qSets[p.k]
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
    
    cltTimer.endTimer(session.cltId, "ProcProof-Clt-LostSum")
       
    
    cltTimer.startTimer(session.cltId, "ProcProof-CreateIbf-From-ProtoBuf") 
    serverStateIbf = session.ibf.generateIbfFromProtobuf(cpdrProofMsg.proof.serverState,
                                                 session.dataBitSize)
    cltTimer.endTimer(session.cltId, "ProcProof-CreateIbf-From-ProtoBuf")

    cltTimer.startTimer(session.cltId, "ProcProof-SubtractIbf")
    diffIbf = session.ibf.subtractIbf(serverStateIbf, session.challenge,
                                      session.sesKey.key.n, session.dataBitSize, True)    
    cltTimer.endTimer(session.cltId, "ProcProof-SubtractIbf")
    
    for k in lostSum.keys():
        val=lostSum[k]
        diffIbf.cells[k].setHashProd(val)
    
    cltTimer.startTimer(session.cltId, "ProcProof-Recover")
    L=CloudPdrFuncs.recover(diffIbf, serverLost, session.challenge, session.sesKey.key.n, session.g)
    cltTimer.endTimer(session.cltId, "ProcProof-Recover")
    
    for k in lostSum.keys():
        print diffIbf.cells[k].hashProd
        
    if L==None:
        print "fail to recover"
    
        
    for blk in L:
        print blk.getDecimalIndex()
      
    return "Exiting Recovery..."

def processClientMessages(incoming, session, cltTimer, lostNum=None):
    
    cpdrMsg = MessageUtil.constructCloudPdrMessageNet(incoming)
    
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT_ACK:
        print "Processing INIT_ACK"
        cltTimer.startTimer(session.cltId, "LossMessage-Create")
        outgoingMsg = MessageUtil.constructLossMessage(lostNum, session.cltId)
        cltTimer.endTimer(session.cltId, "LossMessage-Create")
        return outgoingMsg
        
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.LOSS_ACK:
        print "Processing LOSS_ACK"
        
        cltTimer.startTimer(session.cltId, "ChallengeMsg-Create")
        session.challenge = session.sesKey.generateChallenge()
        outgoingMsg = MessageUtil.constructChallengeMessage(session.challenge, session.cltId)
        cltTimer.endTimer(session.cltId, "ChallengeMsg-Create")
        return outgoingMsg    
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.PROOF:
        print "Received Proof"
        res = processServerProof(cpdrMsg, session, cltTimer)
        print res


def chunks(s, n):
    for start in xrange(0, len(s), n):
        yield s[start:start+n]

def workerTask(inputQueue,W,T,ibf,blockProtoBufSz,blockDataSz,secret,public):
    while True:
        item = inputQueue.get()
        if item == "END":
            return
        
        for blockPBItem in chunks(item, blockProtoBufSz):
            block = BlockEngine.BlockDisk2Block(blockPBItem, blockDataSz)
            bIndex = block.getDecimalIndex()
            print mp.current_process(), "Processing block", bIndex
            w = singleW(block, secret["u"])
            tag = singleTag(w, block, public["g"], secret["d"], public["n"])
            W[bIndex] = w
            T[bIndex] = tag
            ibf.insert(block, None, public["n"], public["g"], True)
            del block
            

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
    pdrSes.addDataBitSize(args.size)
    
    
    
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
    
    genericManager = mp.Manager()
    pdrManager = PdrManager()
    
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
                                               T, cltId, args.hashNum, delta)

    clt = RpcPdrClient()    
    print "Sending Initialization message"
    inComing = clt.rpc("127.0.0.1", 9090, initMsg) 
    print "Received Initialization ACK"

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
#     outgoing = processClientMessages(inComing, pdrSes, cltTimer, args.lostNum)
#     
#     
#     print "Sending Lost message"
#     cltTimer.startTimer(cltId, "Loss-LossAck-RTT")
#     incoming = clt.rpc("127.0.0.1", 9090, outgoing)
#     cltTimer.endTimer(cltId, "Loss-LossAck-RTT")
#     
#     outgoing = processClientMessages(incoming, pdrSes, cltTimer)
#     
#     print "Sending Challenge ...."
#     cltTimer.startTimer(cltId, "Challenge-Proof-RTT")
#     incoming = clt.rpc("127.0.0.1", 9090, outgoing)
#     cltTimer.endTimer(cltId, "Challenge-Proof-RTT")
#     processClientMessages(incoming, pdrSes, cltTimer)
#     
# 
#     cltTimer.printSessionTimers(cltId)



if __name__ == "__main__":
    main()