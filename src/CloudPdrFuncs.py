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

hashFunList = [RSHash, JSHash, 
			PJWHash, ELFHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]



# lostIndeces a list of decimal lost indices

def recover(ibfLost, lostIndices, secret, N, g):
	L = []
	lostPureCells = ibfLost.getPureCells()
	pureCellsNum = len(lostPureCells)
	
	#index=0
	while pureCellsNum > 0:
		cIndex = lostPureCells.pop(0)
		blockIndex =  ibfLost.cells[cIndex].getDataSum().getDecimalIndex()
		#blockRecover = Block(0,0)
		#blockRecover.data = ibfLost.cells[cIndex].getDataSum().data
		#blockRecover.dataBitsize = ibfLost.cells[cIndex].getDataSum().dataBitsize

		
		if blockIndex not in lostIndices:
			return None

		#print blockIndex
		L.append(blockIndex)
		#index=0
		#for block in L:
			#print block.getDecimalIndex()
			#index+=1
		#print index
		#index+=1
		ibfLost.delete(ibfLost.cells[cIndex].getDataSum(), secret, N, g, cIndex)
		lostIndices.remove(blockIndex)
		
		lostPureCells = ibfLost.getPureCells()
		pureCellsNum = len(lostPureCells)
	#for block in L:
		#print block.getDecimalIndex()
	#print L[0].getDecimalIndex()
	#print L[1].getDecimalIndex()
		
	print "Entering Check..."
	for cIndex in xrange(ibfLost.m):
		if ibfLost.cells[cIndex].getCount() != 0:
			print "Failed to recover", "Reason: ", "Count", cIndex
			return None
			
			
		if ibfLost.cells[cIndex].getDataSum().isZeroDataSum() == False:
			print "Failed to recover", "Reason: ", "Datasum", cIndex
			return None
			
		#print ibfLost.cells[cIndex].hashProd
		if  ibfLost.cells[cIndex].getHashProd() !=1:
			print "Failed to recover", "Reason: ", "HashProd", cIndex
			print cIndex
			return None
					
		
	if len(lostIndices) != 0:
		return None
	
	return L
	
	




