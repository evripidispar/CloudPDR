from Crypto.Util import number
from ConfigPDR import GENERATOR_NUM_BITS
from Crypto.Hash import HMAC


def pickGeneratorG(N):


	while True:
		a = number.getRandomRange(0,N)

		if a>n:
			return None
		
		r0 = number.GCD(a,N)
		if r0==1:
			continue
		
		r0 = a-1
		r1 = number.GCD(r0,N)
		if r1 == 1:
			continue

		r0 = a+1
		r1 = nuber.GCD(r0,N)
		if r1 == 1:
			continue 
	g = a**2
	return g


def pickPseudoRandomTheta(secret_key, index):
	hmac = HMAC.new(secret_key)
	hmac.update(index)
	return h.hexdigest()

def generate_f(block, N, index, secret_key):
	index = block.getIndexBytes()
	g = self.pickGeneratorG(N)
	a = self.pickPseudoRandomTheta(secret_key, index)
	aLong = number.bytes_to_long(a)
	bLong = number.bytes_to_long(block.toBytes())
	abExp = aLong*bLong
	return pow(g, abExp, N)

