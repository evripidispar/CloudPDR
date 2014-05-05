import CloudPdrMessages_pb2
from Ibf import Ibf
'''
    @var pub: public key in protocol buffer format
    @var blks: block collection in protocol buffer format
    @var tags: tag collection in protocol buffer format
'''
def constructInitMessage(pub, blks, tags, cltId, k, delta):
    initMsg = CloudPdrMessages_pb2.Init()
    initMsg.pk.CopyFrom(pub)
    initMsg.bc.CopyFrom(blks)
    initMsg.tc.CopyFrom(tags)
    initMsg.k = k
    initMsg.delta = delta
    print delta
    cpdrMsg = constructCloudPdrMessage(CloudPdrMessages_pb2.CloudPdrMsg.INIT,
                                       initMsg, None, None, None, cltId)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg


def constructCloudPdrMessage(msgType, init=None, ack=None, 
                             chlng=None, proof=None,
                            cId=None, loss=None, lossAck=None):
    cpdrMsg = CloudPdrMessages_pb2.CloudPdrMsg()
    cpdrMsg.type = msgType
    
    if init != None:
        cpdrMsg.init.CopyFrom(init)
    if ack != None:
        cpdrMsg.ack.CopyFrom(ack)
    if chlng != None:
        cpdrMsg.chlng.CopyFrom(chlng)
    if proof != None:
        cpdrMsg.proof.CopyFrom(proof)
    if cId != None:
        cpdrMsg.cltId = cId
    if loss != None:
        cpdrMsg.lost.CopyFrom(loss)
    if lossAck != None:
        cpdrMsg.lack.CopyFrom(lossAck)
    
    return cpdrMsg
    

def constructCloudPdrMessageNet(data):
    cpdrMsg = CloudPdrMessages_pb2.CloudPdrMsg()
    cpdrMsg.ParseFromString(data)
    return cpdrMsg


def constructInitAckMessage():
    initAck = CloudPdrMessages_pb2.InitAck()
    initAck.ack = True
    cpdrMsg = constructCloudPdrMessage(CloudPdrMessages_pb2.CloudPdrMsg.INIT_ACK,
                                     None, initAck)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg

def constructChallengeMessage(challenge, cltId):
    chlng = CloudPdrMessages_pb2.Challenge()
    chlng.challenge = str(challenge)
    cpdrMsg = constructCloudPdrMessage(CloudPdrMessages_pb2.CloudPdrMsg.CHALLENGE,
                                       None, None, chlng, None, cltId)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg

def constructLossMessage(lossNum, cId):
    lost= CloudPdrMessages_pb2.Lost()
    lost.lossNum = lossNum
    cpdrMsg = constructCloudPdrMessage(CloudPdrMessages_pb2.CloudPdrMsg.LOSS,
                                       None, None, None, None, cId, lost)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg
    

def constructLostAckMessage():
    lostAck = CloudPdrMessages_pb2.LostAck()
    lostAck.ack = True
    cpdrMsg = constructCloudPdrMessage(CloudPdrMessages_pb2.CloudPdrMsg.LOSS_ACK,
                                       None, None, None, None, None, None, lostAck)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg

def constructProofMessage(combinedSum, combinedTag, ibf, lostIndeces, combinedLostTags):
    proof = CloudPdrMessages_pb2.Proof()
    proof.combinedSum = str(combinedSum)
    proof.combinedTag = str(combinedTag)
    
    #TODO: transform dataSum
    #ibf_bytes = Ibf(ibf.k, ibf.m)
    #print ibf.m
    #for cIndex in range(ibf.m):
        #print(ibf.cells[1].count)
        #ibf_bytes.cells[cIndex].setCount(ibf.cells[cIndex].count)
        #ibf_bytes.cells[cIndex].setHashProd(ibf.cells[cIndex].hashProd)
        #ibf_bytes.cells[cIndex].dataSum = ibf.cells[cIndex].dataSum.tobytes()
    
    #proof.serverState = ibf_bytes
    
    for index in lostIndeces:
        proof.lostIndeces = lostIndeces[index]
    
    
    combinedLostTags_Str={}
    for k in combinedLostTags.keys():
        combinedLostTags_Str[k] = str(combinedLostTags[k])
    proof.p = combinedLostTags_Str
    
    
    cpdrMsg = constructCloudPdrMessage(CloudPdrMessages_pb2.CloudPdrMsg.PROOF,
                                       None, None, None, proof)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg
