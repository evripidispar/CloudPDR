import CloudPdrMessages_pb2

'''
    @var pub: public key in protocol buffer format
    @var blks: block collection in protocol buffer format
    @var tags: tag collection in protocol buffer format
'''
def constructInitMessage(pub, blks, tags):
    initMsg = CloudPdrMessages_pb2.Init()
    initMsg.pk.CopyFrom(pub)
    initMsg.bc.CopyFrom(blks)
    initMsg.tc.CopyFrom(tags)
    return initMsg


def constructCloudPdrMessage(msgType, init=None, ack=None, chlng=None, proof=None):
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
    
    return cpdrMsg
    

def constructCloudPdrMessageNet(data):
    cpdrMsg = CloudPdrMessages_pb2.CloudPdrMsg()
    cpdrMsg.ParseFromString(data)
    return cpdrMsg


def constructInitAckMessage():
    initAck = CloudPdrMessages_pb2.InitAck()
    initAck.ack = True
    cpdrMsg = CloudPdrMessages_pb2.CloudPdrMsg()
    cpdrMsg.type = CloudPdrMessages_pb2.CloudPdrMsg.INIT_ACK
    cpdrMsg.ack.CopyFrom(initAck)
    cpdrMsg = cpdrMsg.SerializeToString()
    return cpdrMsg

def constructChallengeMessage(challenge):
    chlng = CloudPdrMessages_pb2.Challenge()
    chlng.challenge = str(challenge)
    cpdrMsg = CloudPdrMessages_pb2.CloudPdrMsg()
    cpdrMsg.type = CloudPdrMessages_pb2.CloudPdrMsg.CHALLENGE
    cpdrMsg.chlng.CopyFrom(chlng)
    return cpdrMsg
