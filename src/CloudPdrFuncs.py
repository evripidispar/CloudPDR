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
		if cell.isEmpty() == False:
			cell.printSelf()
			return None
		#In recover algorithm the paper has:
		# if cell.getCount() != 0:
		# 	return False
		# if cell.getDataSum() != 0:
		# 	return False
		# if cell.getHashProd() != 1:
		# 	return False

	if len(lostIndeces) != 0:
		return None


	return L
 			


