from Crypto.Util import number
from Crypto.Hash import HMAC


def pickPseudoRandomTheta(secret_key, index):
	hmac = HMAC.new(secret_key)
	hmac.update(index)
	return hmac.hexdigest()

def generate_f(block, N, secret_key, g):
	index = block.getStringIndex()
	a = pickPseudoRandomTheta(secret_key, index)
	aLong = number.bytes_to_long(a)
	bLong = number.bytes_to_long(block.data.tobytes())
	abExp = aLong*bLong
	return pow(g, abExp, N)

