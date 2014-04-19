import Ibf
from HashFunc import *

hashFunList = [RSHash, JSHash, 
			PJWHash, ELFHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]


#TODO: No idea why you want the list of hashFunctions as
# an argument here
# lostIndeces: a list with the lost indeces as strings 

def recover(ibfLost, lostIndeces, hashFunList):

	L = []
	lostPureCells = ibfLost.getPureCells()
	for cell in lostPureCells:
		blockIndex =  cell.getDataSum().getIndex()
		if blockIndex not in lostIndeces:
			return None
		
		L.append(cell.getDataSum())
		ibfLost.delete(cell.getDataSum)

		lostIndeces.remove(blockIndex)

	for cell in ibfLost:
		
		if cell.getCount() != 0 or 
				cell.getDataSum() != Block(0) or
				 cell.getHashProd() !=1:
			cell.printSelf()
			return None

	if len(lostIndeces) != 0:
		return None


	return L
 			


