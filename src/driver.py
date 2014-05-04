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


def produceClientId():
    h = SHA256.new()
    h.update(datetime.now())
    return h.hexdigest()


def processClientMessages(incoming, session):
    cpdrMsg = MessageUtil.constructCloudPdrMessageNet(incoming)
    
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT_ACK:
        session.challenge = session.sesKey.generateChallenge()
        outgoingMsg = MessageUtil.constructChallengeMessage(session.challenge)
        return outgoingMsg
        
        
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.PROOF:
        print "Received Proof"

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
    
    p.add_argument('-d', dest='d', action='store', type=float, default=0.005,
                   help='Delta: number of blocks we can recover')
   

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
        
        
    
    #Create current session
    pdrSes = PdrSession()  
    
    # Read blocks from Serialized file
    blocks = BlockEngine.readBlockCollectionFromFile(args.blkFp)
    pdrSes.blocks = BlockEngine.blockCollection2BlockObject(blocks)
    
    
    #Get Ibf len based on delta, k and number of blocks
    ibfLength = args.delta * len(blocks)
    ibfLength *= (args.k+1)
    
    
    #Read the generator from File
    fp = open(args.genFile, "r")
    g = fp.read()
    g = long(g)
    fp.close() 
    
    
    #Generate client id
    cltId = produceClientId()
   
    #Generate key class
    pdrSes.sesKey = CloudPDRKey(args.n, g)
    secret = pdrSes.sesKey.getSecretKeyFields()
    pubPB = pdrSes.sesKey.getProtoBufPubKey()
    
    #Create the "h" object
    h = SHA256.new()
    
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
    
 
 
    #Construct InitMsg
    initMessage = MessageUtil.constructInitMessage(pubPB, 
                                                   blocks, 
                                                   tagCollection,
                                                   cltId,
                                                   args.k,
                                                   args.d)

    clt = RpcPdrClient()    
    
    print "Sending Init..."
    inComing = clt.rpc("127.0.0.1", 9090, initMessage)
    
    print "Processing Init Ack and producing Lost Message"
    #TODO tell the guy what indeces to lost
    outgoing = processClientMessages(inComing, pdrSes)
    
    
    print "Sending Lost message"
    incoming = clt.rpc("127.0.0.1", 9090, outgoing)
    
    
    print "Sending Challenge ...."
    incoming = clt.rpc("127.0.0.1", 9090, outgoing)
    
    print "Processing proof and determine if server checks out"
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