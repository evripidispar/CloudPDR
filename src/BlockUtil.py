from Crypto import Random
from Crypto.Random import random 
from Block import *
from bitarray import bitarray
import numpy as np


def npArray2bitArray(npArray):
	bit = bitarray()
	bit.pack(npArray.tostring())
	return bit

def createSingleBlock(index, dataSize, pseudoData=None, xrangeObj=None, bits=None):
	newBlock = Block(index, 0)
	data = bitarray()
	if pseudoData == None:
		data = np.random.rand(dataSize*8) < 0.5
		#byteData = Random.get_random_bytes(dataSize)
		#data.frombytes(byteData)
	else:
		data = createSinglePseudoRandomData(pseudoData, xrangeObj, bits)
	
	newBlock.setRandomBlockData2(data)
	return newBlock

def createSinglePseudoRandomData(data, xrangeObj, bits):
	smpl = random.sample(xrangeObj, bits)
	data[smpl]=~data[smpl]
# 	for c in smpl:
# 		if data[c] == True:
# 			data[c]=False
# 		else:
# 			data[c]=True
# 	return data
		


def blockCreatorMemory(howMany, dataSize):
	blocks = []
	for i in xrange(0, howMany):
		newBlock = createSingleBlock(i, dataSize)
		blocks.append(newBlock)
	return blocks
	

def pickCommonBlocks(numOfBlocks, numOfCommon):
	common = random.sample(xrange(numOfBlocks), numOfCommon)
	return common


def pickDiffBlocks(numOfBlocks, common, totalBlocks):
	numDiff = numOfBlocks - len(common)
	
	blocks = range(totalBlocks)

	for block_index in xrange(numOfBlocks):
		if block_index in common:
			blocks.remove(block_index)

	a_diff = random.sample(blocks, numDiff)
	for block_index in a_diff:
		blocks.remove(block_index)


	b_diff = random.sample(blocks, numDiff)
	return (a_diff, b_diff)


