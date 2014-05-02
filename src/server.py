from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet import reactor
import argparse


class CloudPDRProtocol(Protocol):
    
    def __init__(self, factory):
        self.factory = factory
    
    def connectionMade(self):
        print "Connection in ..."
    
    
    def dataReceived(self, data):
        print data
        self.transport.write("Good\n")    
        self.transport.loseConnection()


class CloudPDRFactory(Factory):
    
    def __init__(self):
        print "Init factory "
    
    def buildProtocol(self, addr):
        return CloudPDRProtocol(self)
    


def main():
    
    
    p = argparse.ArgumentParser(description='CloudPDR Server')

    p.add_argument('-p', dest='port', action='store', default=9090, type=int,
                   help='CloudPdr server port')
    
    args = p.parse_args()

    reactor.listenTCP(args.port, CloudPDRFactory())
    reactor.run()

    
 



if __name__ == "__main__":
    main()


        
    