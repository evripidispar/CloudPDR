import argparse
import MessageUtil as MU
import zmq
import CloudPdrMessages_pb2
import BlockEngine
from ClientSession import ClientSession
from ExpTimer import ExpTimer
import sys

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
        runId = cpdrMsg.init.runId
        clients[cltName] = ClientSession(N, g, cpdrMsg.init.tc, delta, k, fs, blkNum, runId)
        
    initAck = MU.constructInitAckMessage()
    return initAck

def processChallenge(cpdrMsg):
     
    if cpdrMsg.cltId in clients.keys():
        chlng = cpdrMsg.chlng.challenge
        clients[cpdrMsg.cltId].addClientChallenge(chlng)
        proofMsg  = clients[cpdrMsg.cltId].produceProof(cpdrMsg.cltId)
        return proofMsg

def processLostMessage(cpdrMsg):
    
    print "Processing Lost Message"
    lossNum = cpdrMsg.lost.lossNum
    if cpdrMsg.cltId in clients.keys():
        clients[cpdrMsg.cltId].chooseBlocksToLose(lossNum)
    
    #Just generate a loss ack
    lossAck = MU.constructLostAckMessage()
    return lossAck

def procMessage(incoming):
    
    print "Processing incoming message..."
    
    cpdrMsg = MU.constructCloudPdrMessageNet(incoming)
    
    
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT:
        initAck = processInitMessage(cpdrMsg)
        return initAck
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.LOSS:
        lossAck = processLostMessage(cpdrMsg)
        return lossAck
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.CHALLENGE:
        print "Incoming challenge"
        proof = processChallenge(cpdrMsg)
        return proof
    
    
        
        
def serve(port):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:"+str(port))

    while True:
        msg = socket.recv()
        outMessage = procMessage(msg)
        socket.send(outMessage)

def main():
    
    p = argparse.ArgumentParser(description='CloudPDR Server')

    p.add_argument('-p', dest='port', action='store', default=9090,
                   help='CloudPdr server port')
    
    args = p.parse_args()
    
    
    serve(args.port)

if __name__ == "__main__":
    main()


        
    