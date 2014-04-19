from bitarray import bitarray
from ConfigPDR import ID_LEN

class Block(object):

	def __init__(self,id):
		util_id = self.idToBinary(id)
		id_len = ID_LEN-len(util_id)
		self.data = id_len * bitarray('0')
		self.data.extend(util_id)
		
	def idToBinary(self,id):
		bit_id="{0:b}".format(id)
		return bit_id
	
	def setRandomBlockData(self, blockData):
		self.data.extend(blockData)
	
	def addBlockData(self, otherBlock):
		self.data = self.data ^ otherBlock.data
			
	def getIndex(self):
		return self.data[0:ID_LEN]

	def getIndexBytes(self):
		return self.data[0:ID_LEN].tobytes()

	def getData(self):
		return self.data[ID_LEN:]

	def getDemicalIndex(self):
		return int(self.getIndex, 2)
