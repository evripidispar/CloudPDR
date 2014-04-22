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


	def insert(self, block, secret, N):
		blockIndeces = self.getIndeces(block)
		print blockIndeces
		for i in blockIndeces:
			if i not in self.cells.keys():
				self.cells[i]=Cell()
				self.cells[i].dataSum.setBlockData(block)
			else:
				self.cells[i].add(block, secret, N)

		
	def delete(self, block):
		blockIndeces =  self.getIndeces(block)
		for i in blockIndeces:
			#TODO: no idea what's up if the block is not inside the Cell
			if self.cell[i].isEmpty == False:
				self.cell[i].delete(block, secret, N)


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
		for cell in self.cells:
			if cell.isPure():
				pureCells.append(cell)
		return pureCells


	def findBlock(self,block):
		indeces = self.getIndeces(block)
		for i in blockIndeces:
			if self.cells[i].isEmpty():
				return False
		return True


