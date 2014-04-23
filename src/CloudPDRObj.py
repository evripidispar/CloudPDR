from Crypto.Util import number 
from Crypto.Hash import HMAC

class CloudPDRObj(object):
	
	def __init__(self, Nbits, filename):	
		self.N = number.getRandomInteger(Nbits)
		self.secret = self.generateSecret(Nbits)
		if filename == None:
			self.g = self.pickGeneratorG()
			fp = open(filename, "w")
			fp.write(self.g)
			fp.close()
		else:
			fp = open(filename, "r")
			self.g = fp.read()
			self.g = long(self.g)
			

	def generateSecret(self,Nbits):
		tmpRand = number.getRandomInteger(Nbits)
		h = HMAC.new(str(self.N))
		h.update(str(tmpRand))
		return h.hexdigest()

	def pickGeneratorG(self):
		print "Entering pickGenerator"
		while True:
			a = number.getRandomRange(0,self.N)
			if a>self.N:
				return None
			r0 = number.GCD(a,self.N)
			if r0==1:
				continue
		
			r0 = a-1
			r1 = number.GCD(r0,self.N)
			if r1 == 1:
				continue

			r0 = a+1
			r1 = number.GCD(r0,self.N)
			if r1 == 1:
				continue
			break
		g = a**2
		print "Exiting pickGenerator"
		return g

