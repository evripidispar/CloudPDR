import argparse
import sys
from BlockUtil import *
from Ibf import *
#from CloudPDRObj import *
#import CloudPdrFuncs
import BlockEngine
from CloudPDRKey import CloudPDRKey
from TagGenerator import TagGenerator
from Crypto.Hash import SHA256
from datetime import datetime
import MessageUtil
import CloudPdrMessages_pb2
from client import RpcPdrClient
from PdrSession import PdrSession
from math import floor
from math import log
from CryptoUtil import pickPseudoRandomTheta
from Crypto.Util import number

def produceClientId():
    h = SHA256.new()
    h.update(str(datetime.now()))
    return h.hexdigest()


def processServerProof(cpdrProofMsg, session):
    serverLost =  set()
    
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
    
        serCombinedSum = long(cpdrProofMsg.proof.combinedSum)
        gS = pow(session.g, serCombinedSum, session.sesKey.key.n)
        serCombinedTag = long(cpdrProofMsg.proof.combinedTag)
        SesSecret = session.sesKey.getSecretKeyFields() 
        
        Te =pow(serCombinedTag, SesSecret["e"], session.sesKey.key.n)
        
        #print session.g
        #print serCombinedTag
        #print serCombinedSum
        
        index = 0
        combinedW=1
        for blk in session.blocks:
            if index in cpdrProofMsg.proof.lostIndeces:
                index+=1
                continue
            
            aBlk = pickPseudoRandomTheta(session.challenge, blk.getStringIndex())
            aI = number.bytes_to_long(aBlk)
            #print aI
            
            w = session.W[index]
            session.h.update(str(w))
            wHash = number.bytes_to_long(session.h.digest())
            wa= pow(wHash, aI, session.sesKey.key.n)
            combinedW = pow((combinedW*wa), 1, session.sesKey.key.n)
            index+=1
            
        
        combinedWInv = number.inverse(combinedW, session.sesKey.key.n)  #TODO: Not sure this is true
        RatioCheck1=Te*combinedWInv
        RatioCheck1 = pow(RatioCheck1, 1, session.sesKey.key.n)
        
        if RatioCheck1 != gS:
            print "FAIL#3: The Proof did not pass the first check to go to recover"
            return False



def processClientMessages(incoming, session):
    cpdrMsg = MessageUtil.constructCloudPdrMessageNet(incoming)
    
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT_ACK:
        print "Processing INIT_ACK"
        outgoingMsg = MessageUtil.constructLossMessage(3, session.cltId)
        return outgoingMsg
        
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.LOSS_ACK:
        print "Processing LOSS_ACK"
        session.challenge = session.sesKey.generateChallenge()
        #print session.challenge
        outgoingMsg = MessageUtil.constructChallengeMessage(session.challenge, session.cltId)
        return outgoingMsg    
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.PROOF:
        print "Received Proof"
        processServerProof(cpdrMsg, session)

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
    
    #p.add_argument('-d', dest='delta', action='store', type=float, default=0.005,
    #               help='Delta: number of blocks we can recover')
   

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
    
    # Read blocks from Serialized file
    blocks = BlockEngine.readBlockCollectionFromFile(args.blkFp)
    pdrSes.blocks = BlockEngine.blockCollection2BlockObject(blocks)
    
    
    #Get Ibf len based on delta, k and number of blocks
    
    ibfLength =  floor(log(len(pdrSes.blocks),2)) 
    ibfLength *= (args.hashNum+1)
    ibfLength = int(ibfLength)
    
    
    #Read the generator from File
    fp = open(args.genFile, "r")
    g = fp.read()
    g = long(g)
    fp.close() 
    pdrSes.addG(g)
    
   
    #Generate key class
    pdrSes.sesKey = CloudPDRKey(args.n, g)
    secret = pdrSes.sesKey.getSecretKeyFields()
    pdrSes.addSecret(secret)
    pubPB = pdrSes.sesKey.getProtoBufPubKey()
    
    #Create the "h" object
    h = SHA256.new()
    pdrSes.addh(h)
    #Create a tag generator
    tGen = TagGenerator(h)
    wStartTime = datetime.now()
    
    #Create Wi
    pdrSes.W = tGen.getW(pdrSes.blocks, secret["u"])
    wEndTime = datetime.now()
    
    #Create Tags
    tagStartTime = datetime.now()
    T = tGen.getTags(pdrSes.W, g, pdrSes.blocks, secret["d"], pdrSes.sesKey.key.n)
    tagEndTime = datetime.now()
    tagCollection = tGen.createTagProtoBuf(T)
    print "W creation:" , wEndTime-wStartTime
    print "Tag creation:" , tagEndTime-tagStartTime
    
 
 
    #Create the local state
    clientIbf = Ibf(args.hashNum, ibfLength)
    clientIbf.zero(blocks.blockBitSize)
    for blk in pdrSes.blocks:
        clientIbf.insert(blk, None, pdrSes.sesKey.key.n, g, True)
 
    pdrSes.addState(clientIbf)
    
 
    #Construct InitMsg
    log2Blocks = log(len(pdrSes.blocks), 2)
    log2Blocks = floor(log2Blocks)
    delta = int(log2Blocks)
    pdrSes.addDelta(delta)
    
    
    initMessage = MessageUtil.constructInitMessage(pubPB, 
                                                   blocks, 
                                                   tagCollection,
                                                   cltId,
                                                   args.hashNum,
                                                   delta)

    clt = RpcPdrClient()    
    
    print "Sending Init..."
    inComing = clt.rpc("127.0.0.1", 9090, initMessage)
    outgoing = processClientMessages(inComing, pdrSes)
    
    
    print "Sending Lost message"
    incoming = clt.rpc("127.0.0.1", 9090, outgoing)
    outgoing = processClientMessages(incoming, pdrSes)
    
    print "Sending Challenge ...."
    incoming = clt.rpc("127.0.0.1", 9090, outgoing)
    processClientMessages(incoming, pdrSes)
    
    
    
    
    
 
   
#    commonBlocks = pickCommonBlocks(args.numBlocks, args.numCommon)
#    diff_a, diff_b = pickDiffBlocks(args.numBlocks, commonBlocks, args.totalBlocks)
#   
#
#     ibfA = Ibf(args.hashNum, args.ibfLen)
#     ibfA.zero(args.dataSize)
#     ibfB = Ibf(args.hashNum, args.ibfLen)
#     ibfB.zero(args.dataSize)
# 
#     for cBlock in commonBlocks:
#         ibfA.insert(blocks[cBlock], cObj.secret, cObj.N, cObj.g, args.dataSize)
#         ibfB.insert(blocks[cBlock], cObj.secret, cObj.N, cObj.g, args.dataSize)
# 
#     for diffBlock in diff_a:
#         ibfA.insert(blocks[diffBlock], cObj.secret, cObj.N, cObj.g, args.dataSize)
# 
#     lostindices=[]
#     #lostindices=diff_a
#     for i in diff_a:
#         lostindices.append(i)
# 
#     for diffBlock in diff_b:
#         ibfB.insert(blocks[diffBlock], cObj.secret, cObj.N, cObj.g,  args.dataSize)
# 
# 
#     for diffBlock in diff_b:
#         ibfB.delete(blocks[diffBlock], cObj.secret, cObj.N, cObj.g)
#         
#     
#     diffIbf = ibfA.subtractIbf(ibfB,  cObj.secret, cObj.N, args.dataSize)
#     for cellIndex in xrange(args.ibfLen):
#         diffIbf.cells[cellIndex].printSelf()
#     
#     #lostindices=diff_a
#     L=CloudPdrFuncs.recover(diffIbf, diff_a, args.dataSize, cObj.secret, cObj.N, cObj.g)
# 
#     if L==None:
#         print "fail to recover"
# 
#     for block in L:
#         print block
# 
#     
#     print len(L)
#     print len(lostindices)
# 
#     recovered=0
#     if(len(L)==len(lostindices)):
#         for i in lostindices:
#             if i in L:
#                 recovered+=1
#                 #print "SUCCESS"
# 
#     print recovered
    
    


if __name__ == "__main__":
    main()