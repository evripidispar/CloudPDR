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


	def getIndeces(self,block):
		indeces = []
		blockIndex = block.getStringIndex()
		for i in range(self.k):
			hashIndexVal = self.HashFunc[i](blockIndex)
			indeces.append(hashIndexVal % self.m)
		return indeces


	def insert(self, block, secret, N, g, dataByteSize):
		blockIndeces = self.getIndeces(block)
		for i in blockIndeces:
			if i not in self.cells.keys():
				self.cells[i]=Cell(0, dataByteSize)
			self.cells[i].add(block, secret, N, g)

		
	def delete(self, block, secret, N, g):
		blockIndeces =  self.getIndeces(block)
		for i in blockIndeces:
			#TODO: no idea what's up if the block is not inside the Cell
			if self.cells[i].isEmpty() == False:
				self.cells[i].remove(block, secret, N, g)


	def subtract(self, otherIbf, secret, N):
		if self.m != otherIbf.m:
			print "IBFs different sizes"
			return None

		index = 0
		LOCAL = 0
		OTHER = 1
		newIbf = Ibf(self.k, self.m)
		for pair in zip(self.cells, otherIbf.cells):
			newIbf.cells[index] = pair[LOCAL].subtract(pair[OTHER])
			index+=1
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


