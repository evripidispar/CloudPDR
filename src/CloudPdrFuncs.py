from HashFunc import RSHash
from HashFunc import JSHash
from HashFunc import PJWHash
from HashFunc import ELFHash
from HashFunc import BKDRHash
from HashFunc import SDBMHash
from HashFunc import DJBHash
from HashFunc import DEKHash
from HashFunc import BPHash
from HashFunc import FNVHash
from HashFunc import APHash
from Ibf import *
from Block import *
import copy

hashFunList = [RSHash, JSHash, 
			PJWHash, ELFHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]



# lostIndeces a list of decimal lost indices

def recover(ibfLost, lostIndices, secret, N, g):
	L = []
	lostPureCells = ibfLost.getPureCells()
	pureCellsNum = len(lostPureCells)
	

	while pureCellsNum > 0:
		cIndex = lostPureCells.pop(0)
		blockIndex =  ibfLost.cells[cIndex].getDataSum().getDecimalIndex()
		
		
		if blockIndex not in lostIndices:
			return None


		recoveredBlock = copy.deepcopy(ibfLost.cells[cIndex].getDataSum())
		L.append(recoveredBlock)
		
		ibfLost.delete(ibfLost.cells[cIndex].getDataSum(), secret, N, g, cIndex)
		lostIndices.remove(blockIndex)
		
		lostPureCells = ibfLost.getPureCells()
		pureCellsNum = len(lostPureCells)
	
		
	print "Recovery Check..."
	for cIndex in xrange(ibfLost.m):
		if ibfLost.cells[cIndex].getCount() != 0:
			print "Failed to recover", "Reason: ", "Count", cIndex
			return None
			
			
		if ibfLost.cells[cIndex].getDataSum().isZeroDataSum() == False:
			print "Failed to recover", "Reason: ", "Datasum", cIndex
			return None
			
		if  ibfLost.cells[cIndex].getHashProd() !=1:
			print "Failed to recover", "Reason: ", "HashProd", cIndex
			print cIndex
			return None
					
		
	if len(lostIndices) != 0:
		return None
	
	return L
	
	




