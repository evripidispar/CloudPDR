import zmq

class RpcPdrClient(object):
    
    def __init__(self):
        self.context = zmq.Context()
    
    def rpc(self, ip, port, msg):
        sock = self.context.socket(zmq.REQ)
        sock.connect("tcp://"+str(ip)+":"+str(port))
        sock.send(msg)
        
        inMsg = sock.recv()
        return inMsg
        

