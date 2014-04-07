from bitarray import bitarray

ID_LEN = 32

class Block(object):

	def __init__(self,id):
		util_id = id2bit(id)
		id_len = ID_LEN- len(util_id)
		self.data = id_len * bitarray('0')
		self.data.extend(util_id)
		
	def id2bit(id):
		bit_id="{0:b}".format(id)
		return bit_id
	

	def setRandomBlockData(self, blockData):
		self.data.extend(blockData)
	
	def addBlockData(self, otherBlock):
		self.data = self.data ^ otherBlock.data
			
	def getIndex(self):
		return self.data[0:ID_LEN]

	def getData(self):
		return self.data[ID_LEN:]

if __name__ == "__main__":
	main()