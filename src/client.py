from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
import argparse


class CloudPDRClientProtocol(Protocol):
    
    
    def __init__(self, msg):
        self.msg = msg
    
    def connectionMade(self):
        self.sendMessage(self.msg)
    
    def sendMessage(self, msg):
        self.transport.write(msg)
    
    def dataReceived(self, data):
        print "Received:" , data
        self.transport.loseConnection()
    
class CloudPDRClientFactory(ClientFactory):
    
    
    def __init__(self, msg):
        self.msg = msg
    
    def buildProtocol(self,addr):
        protocol = CloudPDRClientProtocol(self.msg)
        protocol.factory = self    
        return protocol

    def clientConnectionLost(self, connector, reason):
        print "Connection closed"
        reactor.stop()
    
    
    
def main():
    p = argparse.ArgumentParser(description='CloudPDR Server')

    p.add_argument('-i', dest='host', action='store', default="127.0.0.1",
                   help='CloudPdr server IP address')

    p.add_argument('-p', dest='port', action='store', default=9090, type=int,
                   help='CloudPdr server port')
    
    
    args = p.parse_args()
    
    factory = CloudPDRClientFactory("Message From client")
    reactor.connectTCP(args.host, args.port, factory)
    reactor.run()
    
    

if __name__ == "__main__":
    main()

