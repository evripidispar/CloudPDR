from Crypto.Util import number
from Block import *
from CryptoUtil import *

class Cell(object):
	def __init__(self, id, dataByteSize):
		self.count = 0
		self.dataSum = Block(id, dataByteSize*8)
		self.hashProd = 1
		self.f = 0

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


	def add(self, block, secret, N, g):
		self.count += 1
		self.dataSum.addBlockData(block)
		f = generate_f(block, N, secret, g)
		self.f = f
		self.hashProd *= f
		self.hashProd = pow(self.hashProd, 1, N)
		return

	def remove(self, block, secret, N, g):
		#TODO
		#count handling
		if (self.count < 0):
			self.count += 1
		else:
			self.count -= 1

		self.dataSum.addBlockData(block)
		f = generate_f(block, N, secret, g)
		fInv = number.inverse(f, N)  #TODO: Not sure this is true
		self.hashProd *= fInv
		self.hashProd = pow(self.hashProd, 1, N)

	def isPure(self):  #Read Babis 1 or -1

		if self.count == 1:  #TODO:  is this correct?
			return True
		return False

	def isEmpty(self):
		if self.count == 0:
			return True
		return False

	def subtract(self, otherCell, dataByteSize, N):
		diffCell = Cell(0, dataByteSize)
		
		#counter
		diffCell.count = self.count - otherCell.getCount()
		
		#datasum
		localDS = self.getDataSum().getWholeBlockBitArray()
		otherDS = otherCell.getDataSum().getWholeBlockBitArray()
		diffCell.setDataSum(localDS ^ otherDS)
		
		#hashProd
		
		if (number.GCD(otherCell.getHashProd(), N)!=1):
			print "Problem"
		otherFInv = number.inverse(otherCell.getHashProd(), N)
		diffCell.hashProd = otherFInv * self.hashProd
		print "Before", diffCell.hashProd
		#diffCell.hashProd = pow(diffCell.hashProd, 1, N) 
		
		diffCell.hashProd = diffCell.hashProd % N 
		
		print "After", diffCell.hashProd
		
		if diffCell.hashProd != 1:
			print "-----------"
		else:
			print "-----------"
			
		return diffCell

	def printSelf(self):
		print "Count: " + str(self.count)
		print "DataSum: " + str(self.dataSum)
		print "HashProd: " + str(self.hashProd)


