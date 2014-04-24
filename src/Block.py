from bitarray import bitarray
from ConfigPDR import ID_LEN


class Block(object):
	def __init__(self, id, dataBitSize):
		util_id = self.idToBinary(id)
		id_len = ID_LEN - len(util_id)
		self.data = bitarray(id_len*'0')
		self.data.extend(util_id)
		self.data.extend(dataBitSize*'0')

	def idToBinary(self, id):
		bit_id = "{0:b}".format(id)
		return bit_id

	def setBlockData(self, blockData):
		self.data = blockData.data


	def setRandomBlockData(self, blockData):
		self.data.extend(blockData)

	def addBlockData(self, otherBlock):
		assert self.data.length() == otherBlock.data.length()
		self.data = self.data ^ otherBlock.data

	def getIndex(self):
		return self.data[0:ID_LEN]

	def getIndexBytes(self):
		return self.data[0:ID_LEN].tobytes()

	def getData(self):
		return self.data[ID_LEN:]

	def getWholeBlockBitArray(self):
		return self.data

	def getDecimalIndex(self):
		return int(self.getStringIndex(), 2)
	
	def getStringIndex(self):
		index = self.data[0:ID_LEN]
		indexStr = index.to01()
		return indexStr