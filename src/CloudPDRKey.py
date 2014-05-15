import CloudPdrMessages_pb2
from Crypto.PublicKey import RSA
from Crypto.Util import number
from Crypto.Hash import SHA256


class CloudPDRKey(object):
    '''
    Cloud PDR central Key structure. It generates the public key we send
    to the server
    '''
    
    def __init__(self, mSize, g):
        self.key = RSA.generate(mSize)
        self.g = g
        self.pubKeySerialized = None
        self.h = SHA256.new()
        self.mSize = mSize
            
    
    def getProtoBufPubKey(self):
        pubKey = CloudPdrMessages_pb2.PublicKey()
        pubKey.n = str(self.key.n)
        pubKey.g = str(self.g)        
        return pubKey
    
    def getProtoBufPubKeySerialized(self):
        
        if self.pubKeySerialized == None:
            pubKey = self.getProtoBufPubKey()
            self.pubKeySerialized = pubKey.SerializeToString()
        
        return self.pubKeySerialized
        
    def getPublicKeyFields(self):
        public = {}
        public["g"] = self.g
        public["n"] = self.key.n
        return public
    
    
    def getSecretKeyFields(self):
        secret = {}
        secret["e"] = self.key.e
        secret["d"] = self.key.d
        secret["u"] = self.key.u
        return secret
    
    def overwriteKeyFields(self, loadedFields):
        self.g = loadedFields["g"]
        self.key.n = loadedFields["n"]
        self.key.u = loadedFields["u"]
        self.key.d = loadedFields["d"]
        self.key.e = loadedFields["e"]
    
    def generateChallenge(self):
        challenge = number.getRandomInteger(self.mSize)
        return bin(challenge)
    
    
        