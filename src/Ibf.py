from HashFunc import *
from Cell import *

class Ibf(object):
	
	def __init__(self, k, m):
		self.k = k
		self.m = m
		self.cells = {}
		self.HashFunc = [RSHash, JSHash, 
			PJWHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]
		


	def getIndeces(self, block):
		indeces = []
		blockIndex = block.getStringIndex()
		for i in range(self.k):
			hashIndexVal = self.HashFunc[i](blockIndex)
			indeces.append(hashIndexVal % self.m)
		return indeces


	def zero(self,  dataByteSize):
		for cellIndex in xrange(self.m):
			self.cells[cellIndex] = Cell(0, dataByteSize)

	def insert(self, block, secret, N, g, dataByteSize):
		blockIndeces = self.getIndeces(block)
		for i in blockIndeces:
			self.cells[i].add(block, secret, N, g)

		
	def delete(self, block, secret, N, g):
		blockIndeces =  self.getIndeces(block)
		for i in blockIndeces:
			if self.cells[i].isEmpty() == False:
				self.cells[i].remove(block, secret, N, g)


	def subtractIbf(self, otherIbf, secret, N, dataByteSize):
		if self.m != otherIbf.m:
			print "IBFs different sizes"
			return None

		newIbf = Ibf(self.k, self.m)
		for cIndex in range(self.m):
			newIbf.cells[cIndex]= self.cells[cIndex].subtract(otherIbf.cells[cIndex], dataByteSize, N)
		return newIbf

	def getPureCells(self):
		pureCells = []
		for key in self.cells.keys():
			if self.cells[key].isPure():
				pureCells.append(key)
		return pureCells


	def findBlock(self,block):
		indeces = self.getIndeces(block)
		for i in indeces:
			if self.cells[i].isEmpty():
				return False
		return True


