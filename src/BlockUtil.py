import string
from Crypto import Random
from Crypto.Random import random 
from Block import *
from bitarray import bitarray

def blockCreatorMemory(howMany, dataSize):
	blocks = []
	for i in range(0, howMany):
		newBlock = Block(i, 0)
		data = bitarray()
		byteData = Random.get_random_bytes(dataSize)
		data.frombytes(byteData)
		newBlock.setRandomBlockData(data)
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


