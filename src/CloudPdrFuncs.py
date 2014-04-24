from HashFunc import *
from Ibf import *

hashFunList = [RSHash, JSHash, 
			PJWHash, ELFHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]



# lostIndeces a list of decimal lost indices

def recover(ibfLost, lostIndices, dataByteSize, secret, N, g):
	L = []
	lostPureCells = ibfLost.getPureCells()
	for cell in lostPureCells:
		blockIndex =  ibfLost.cells[cell].getDataSum().getDecimalIndex()
		if blockIndex not in lostIndices:
			return None
		
		L.append(ibfLost.cells[cell].getDataSum())
		ibfLost.delete(ibfLost.cells[cell].getDataSum(), secret, N, g)
		lostIndices.remove(blockIndex)
		
		for cIndex in xrange(ibfLost.m):
			if ibfLost.cells[cIndex].getCount() != 0 or \
				ibfLost.cells[cIndex].getDataSum() != Block(0, dataByteSize*8) or \
					 ibfLost.cells[cIndex].getHashProd() !=1:
				ibfLost.cells[cIndex].printSelf()
				return None
		
		if len(lostIndices) != 0:
			return None
	return L
	
	




