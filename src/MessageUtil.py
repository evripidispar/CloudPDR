import CloudPdrMessages_pb2

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
