import argparse
import MessageUtil as MU
import zmq
import CloudPdrMessages_pb2
import BlockEngine
from ClientSession import ClientSession
from ExpTimer import ExpTimer

clients = {}

def processInitMessage(cpdrMsg, storeBlocks=None):
    
    print "Processing Init Message"
    cltName = cpdrMsg.cltId
    if cltName not in clients.keys():
        N = long(cpdrMsg.init.pk.n)
        g = long(cpdrMsg.init.pk.g)
        delta = cpdrMsg.init.delta
        k = cpdrMsg.init.k
        fs = cpdrMsg.init.filesystem
        blkNum = cpdrMsg.init.fsNumBlocks
        clients[cltName] = ClientSession(N, g, cpdrMsg.init.tc, delta, k, fs, blkNum)
        
    initAck = MU.constructInitAckMessage()
    return initAck

def processChallenge(cpdrMsg,serverTimer):
     
    if cpdrMsg.cltId in clients.keys():
        chlng = cpdrMsg.chlng.challenge
        clients[cpdrMsg.cltId].addClientChallenge(chlng)
        proofMsg = clients[cpdrMsg.cltId].produceProof(serverTimer, cpdrMsg.cltId)
        return proofMsg

def processLostMessage(cpdrMsg):
    
    print "Processing Lost Message"
    lossNum = cpdrMsg.lost.lossNum
    if cpdrMsg.cltId in clients.keys():
        clients[cpdrMsg.cltId].chooseBlocksToLose(lossNum)
    
    #Just generate a loss ack
    lossAck = MU.constructLostAckMessage()
    return lossAck

def procMessage(incoming, serverTimer):
    
    print "Processing incoming message..."
    
    cpdrMsg = MU.constructCloudPdrMessageNet(incoming)
    if cpdrMsg.cltId not in serverTimer.timers.keys():
        serverTimer.registerSession(cpdrMsg.cltId)
        serverTimer.registerTimer(cpdrMsg.cltId, "Server-ProcInit")
        serverTimer.registerTimer(cpdrMsg.cltId, "Server-ProcLoss")
        serverTimer.registerTimer(cpdrMsg.cltId, "Server-ProofProtoBufConstruct")
        serverTimer.registerTimer(cpdrMsg.cltId, "Server-ProofCombinedValues")
        serverTimer.registerTimer(cpdrMsg.cltId, "Server-ProofIbfInsert")
        serverTimer.registerTimer(cpdrMsg.cltId, "Server-ProofCombinedLostTags")
    
    
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT:
        serverTimer.startTimer(cpdrMsg.cltId, "Server-ProcInit")
        initAck = processInitMessage(cpdrMsg)
        serverTimer.endTimer(cpdrMsg.cltId, "Server-ProcInit")
        return initAck
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.LOSS:
        serverTimer.startTimer(cpdrMsg.cltId, "Server-ProcLoss")
        lossAck = processLostMessage(cpdrMsg)
        serverTimer.endTimer(cpdrMsg.cltId, "Server-ProcLoss")
        return lossAck
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.CHALLENGE:
        print "Incoming challenge"
        proof = processChallenge(cpdrMsg, serverTimer)
        return proof
    
    
        
        
def serve(port, serverTimer):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:"+str(port))

    while True:
        msg = socket.recv()
        outMessage = procMessage(msg, serverTimer)
        socket.send(outMessage)

def main():
    
    p = argparse.ArgumentParser(description='CloudPDR Server')

    p.add_argument('-p', dest='port', action='store', default=9090,
                   help='CloudPdr server port')
    
    serverTimer = ExpTimer()
    args = p.parse_args()
    serve(args.port, serverTimer)

if __name__ == "__main__":
    main()


        
    