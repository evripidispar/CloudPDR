from HashFunc import *
from Cell import Cell

class Ibf(object):
	
	def __init__(self, k, m):
		self.k = k
		self.m = m
		self.cells = {}
		self.HashFunc = [RSHash, JSHash, 
			PJWHash, BKDRHash, SDBMHash, 
			DJBHash, DEKHash, BPHash, FNVHash, APHash]
		

	def getIndices(self, block, isIndex=False):
		indices = []
		if isIndex == False:
			blockIndex = block.getStringIndex()
		else:
			blockIndex = block #Cases coming from the proof part of the algorithm
			
		for i in range(self.k):
			hashIndexVal = self.HashFunc[i](blockIndex)
			indices.append(hashIndexVal % self.m)
		return indices


	def zero(self,  dataByteSize):
		for cellIndex in xrange(self.m):
			self.cells[cellIndex] = Cell(0, dataByteSize)

	def insert(self, block, secret, N, g, dataByteSize, isHashProdOne=False):
		blockIndices = self.getIndices(block)
		for i in blockIndices:
				self.cells[i].add(block, secret, N, g, isHashProdOne)
			

		
	def delete(self, block, secret, N, g, selfIndex=-1):
		blockIndices =  self.getIndices(block)
		for i in blockIndices:
			if i == selfIndex:
				continue
				
			if self.cells[i].isEmpty() == False:
				self.cells[i].remove(block, secret, N, g)
		
		#TODO: super scary
		if selfIndex != -1:
			self.cells[selfIndex].zeroCell()

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
		indices = self.getIndices(block)
		for i in indices:
			if self.cells[i].isEmpty():
				return False
		return True


