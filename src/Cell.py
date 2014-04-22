from CryptoUtil import number
from Block import *
from CryptoUtil import *

class Cell(object):
	def __init__(self, id=0):
		self.count = 0
		self.dataSum = Block(id)
		self.hashProd = 1

	def setCount(count):
		self.count = count

	def setHashProd(hashProd):
		self.hashProd = hashProd

	def setDataSum(dataSum):
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

	def subtract(self, otherCell):
		#TODO
		diffCell = Cell()
		c = self.count - otherCell.getCount()
		hp = self.modDivision(self.hashProd, otherCell.getHashProd)  #TODO: modDivision
		dS = self.dataSum - otherCell.getDataSum()  #TODO

		diffCell.setCount(c)
		diffCell.setDataSum(ds)
		diffCell.setHashProd(hp)

		return diffCell

	def printSelf(self):
		print "Count: " + self.count
		print "DataSum: " + self.dataSum
		print "HashProd: " + self.hashProd


