import argparse
import MessageUtil
import zmq
import CloudPdrMessages_pb2


def processInitMessage(cpdrMsg, clientSession):
    
    #TODO store info about the client
    #Things like storing to S3 etc should be here
    
    #Just ack that you got the message
    outgoing = MessageUtil.constructInitAckMessage()
    return outgoing

def processChallenge(cpdrMsg, clientSession):
    print "Produce the proof"
    return "proof"


def processLost(cpdrMsg, clientSession):
    print "Process Lost message"
    outgoing = MessageUtil.constructLostAckMessage()
    return outgoing

def procMessage(incoming, clientSession):
    
    print "Processing incoming message..."
    
    cpdrMsg = MessageUtil.constructCloudPdrMessageNet(incoming)
    if cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.INIT:
        outgoing = processInitMessage(cpdrMsg)
        return outgoing
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.CHALLENGE:
        print "Incoming challenge"
        proof = processChallenge(cpdrMsg)
        return proof
    
    elif cpdrMsg.type == CloudPdrMessages_pb2.CloudPdrMsg.LOSS:
        
        
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


        
    