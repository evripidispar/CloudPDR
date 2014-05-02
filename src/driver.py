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
import CloudPdrMessages_pb2
from client import requestReply


def main():
    
    p = argparse.ArgumentParser(description='Driver for IBF')

    
    p.add_argument('-b', dest='blkFp', action='store', default=None,
                   help='Serialized block filename as generated from BlockEngine')
    
    
    p.add_argument('-m', dest='ibfLen', action='store', type=int,
                   default=500, help='Length of the bloom filter')
    
    p.add_argument('-k', dest='hashNum', action='store', type=int,
                   default=5, help='Number of hash arguments')
    
    p.add_argument('-g', dest="genFile", action="store", default=None,
                 help="static generator file")

    
    p.add_argument('-n', dest='n', action='store', type=int,
                   default=1024, help='RSA modulus size')
    

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
        
    
 
    
    #Construct the init message   / Read blocks from Serialized file
    #initMsg = CloudPdrMessages_pb2.Init()
    #TODO: CloudPdr must be constructed bottom up
    
    
    blocks = BlockEngine.readBlockCollectionFromFile(args.blkFp)
    blockObjects = BlockEngine.blockCollection2BlockObject(blocks)
    
    #Read the generator from File
    fp = open(args.genFile, "r")
    g = fp.read()
    g = long(g)
    fp.close() 
    
   
    #Generate key class
    pdrKey = CloudPDRKey(args.n, g)
    secret = pdrKey.getSecretKeyFields()
    
    #Create the "h" object
    h = SHA256.new()
    
    #Create a tag generator
    tGen = TagGenerator(h)
    
    
    wStartTime = datetime.now()
    #Create Wi
    W = tGen.getW(blockObjects, secret["u"])
    wEndTime = datetime.now()
    
    #Create Tags
    tagStartTime = datetime.now()
    T = tGen.getTags(W, g, blockObjects, secret["d"], pdrKey.key.n)
    tagEndTime = datetime.now()
    print "W creation:" , wEndTime-wStartTime
    print "Tag creation:" , tagEndTime-tagStartTime
 
 
    #Construct the rest of the InitMsg
#     initMsg.pk.n = str(pdrKey.key.n)
#     initMsg.pk.g = str(pdrKey.g)   
#     for tag in T:
#         initMsg.tc.tags.append(str(tag))
#         
#     
#    
#     
#     
    #Construct the CloudPdrMsg
    #pdrMsg = CloudPdrMessages_pb2.CloudPdrMsg()
    #pdrMsg.type = pdrMsg.INIT
    #pdrMsg.init = initMsg
    #pdrMsg = pdrMsg.SerializeToString()
    
    
    #RPC to send/rcv the init/initAck 
    msg = requestReply('127.0.0.1', 9090, pdrMsg)
    
    
    
    
 
   
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