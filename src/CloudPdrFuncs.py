from HashFunc import *
from Ibf import *

hashFunList = [RSHash, JSHash, 
			PJWHash, ELFHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]



# lostIndeces a list of decimal lost indices

def recover(ibfLost, lostIndices, dataByteSize, secret, N, g):
	L = []
	lostPureCells = ibfLost.getPureCells()
	pureCellsNum = len(lostPureCells)
	
	while pureCellsNum > 0:
		cIndex = lostPureCells.pop(0)
		blockIndex =  ibfLost.cells[cIndex].getDataSum().getDecimalIndex()
		if blockIndex not in lostIndices:
			return None

		
		L.append(blockIndex)
		ibfLost.delete(ibfLost.cells[cIndex].getDataSum(), secret, N, g, cIndex)
		lostIndices.remove(blockIndex)
		
		lostPureCells = ibfLost.getPureCells()
		pureCellsNum = len(lostPureCells)
		
		
	for cIndex in xrange(ibfLost.m):
		if ibfLost.cells[cIndex].getCount() != 0:
			print "Failed to recover", "Reason: ", "Count", cIndex
			return None
			
			
		if ibfLost.cells[cIndex].getDataSum().isZeroDataSum() == False:
			print "Failed to recover", "Reason: ", "Datasum", cIndex
			return None
			
		if  ibfLost.cells[cIndex].getHashProd() !=1:
			print "Failed to recover", "Reason: ", "HashProd", cIndex
			return None
					
		
	if len(lostIndices) != 0:
		return None
	
	return L
	
	




