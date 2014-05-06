from Crypto.Util import number
from Block import *
from CryptoUtil import apply_f

class Cell(object):
	def __init__(self, id, dataBitSize):
		self.count = 0
		self.dataSum = Block(id, dataBitSize)
		self.hashProd = 1
		self.f = 0

	def cellFromProtobuf(self, count, hashProd, data):
		self.count = count
		self.hashprod = hashProd
		self.dataSum.data = self.dataSum.data.frombytes(data)
		

	def zeroCell(self):
		self.count=0
		self.dataSum.data.setall(False)
		self.hashProd =  1

	def setCount(self, count):
		self.count = count

	def setHashProd(self, hashProd):
		self.hashProd = hashProd

	def setDataSum(self, dataSum):
		self.dataSum = dataSum

	def getCount(self):
		return self.count

	def getHashProd(self):
		return self.hashProd

	def getDataSum(self):
		return self.dataSum


	def add(self, block, secret, N, g, keepHashProdOne=False):
		self.count += 1
		self.dataSum.addBlockData(block)
		
		if keepHashProdOne == False:
			f = apply_f(block, N, secret, g)
			self.f = f
			self.hashProd *= f
			self.hashProd = pow(self.hashProd, 1, N)
		else:
			self.hashProd = 1
			
			
		return

	def remove(self, block, secret, N, g):
		#TODO
		#count handling
		if (self.count < 0):
			self.count += 1
		else:
			self.count -= 1
		
		if block.isZeroDataSum()==False: #TODO
			self.dataSum.addBlockData(block)
			f = apply_f(block, N, secret, g)
			fInv = number.inverse(f, N)  #TODO: Not sure this is true
			self.hashProd *= fInv
			self.hashProd = pow(self.hashProd, 1, N)
			
	def isPure(self):
		if self.count == 1:  
			return True
		return False

	def isEmpty(self):
		if self.count == 0:
			return True
		return False

	def subtract(self, otherCell, dataBitSize, N, isHashProdOne=False):
		
		diffCell = Cell(0, dataBitSize)
		
		#counter
		diffCell.count = self.count - otherCell.getCount()
		
		#datasum
		diffCell.dataSum.addBlockData(self.getDataSum())
		diffCell.dataSum.addBlockData(otherCell.getDataSum())
		
		#dataSum.addBlockData(localDS ^ otherDS)
		
		#hashProd
		diffCell.hashProd = 1	
		if isHashProdOne == False:
			otherFInv = number.inverse(otherCell.getHashProd(), N)
			diffCell.hashProd = otherFInv * self.hashProd
			diffCell.hashProd = pow(diffCell.hashProd, 1, N) 
		
		return diffCell

	def printSelf(self):
		print "Index:" + str(self.dataSum.getDecimalIndex())
		print "Count: " + str(self.count)
		print "HashProd: " + str(self.hashProd)
		print "DataSum " + str(self.dataSum.getWholeBlockBitArray())
		print "------"


