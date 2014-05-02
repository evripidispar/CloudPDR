from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor

class CloudPDRClientProtocol(Protocol):
    
        
    
    def sendMessage(self, msg):
        self.transport.write(msg)
    
    def dataReceived(self, data):
        print data
    
    
class CloudPDRClientFactory(ClientFactory):
    
    def buildProtocol(self,addr):
        protocol = CloudPDRClientProtocol()
        
        return CloudPDRClientProtocol()


