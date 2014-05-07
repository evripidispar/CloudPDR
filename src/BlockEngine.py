import sys
import CloudPdrMessages_pb2
import BlockUtil
import argparse
import datetime
from Block import Block

TEST = False

def createBlocks(blocksNum, blockSize):
    blocks = BlockUtil.blockCreatorMemory(blocksNum, blockSize)
    return blocks

def createBlockProtoBufs(blocks, blockSize):
    print "Creating protocol buffers...."
    blockCollection = CloudPdrMessages_pb2.BlockCollection()
    blockCollection.blockBitSize = blockSize*8
    for b in blocks:
        pbufBlock = blockCollection.blocks.add()
        pbufBlock.index = b.getStringIndex()
        pbufBlock.data = b.getData().to01()

    return blockCollection


def createBlockProtoBufsDisk(blocks, blockSize):
    blockCollection = CloudPdrMessages_pb2.BlockCollectionDisk()
    blockCollection.blockBitSize = blockSize*8
    for b in blocks:
        pbfBlk = blockCollection.collection.add()
        pbfBlk.blk = b.data.tobytes()
        
    return blockCollection


def readBlockCollectionFromDisk(filename):
    print "Reading block collection from disk (", filename, ")"
    bc = CloudPdrMessages_pb2.BlockCollectionDisk()
    fp = open(filename,"rb")
    bc.ParseFromString(fp.read())
    fp.close()
    return bc

def writeBlockCollectionToFile(filename, blkCollection):
    print "Writing Block Collection to File"
    fp = open(filename, "wb")
    fp.write(blkCollection.SerializeToString())
    fp.close()

def readBlockCollectionFromFile(filename):
    print "Reading Block collection from File"
    blockCollection = CloudPdrMessages_pb2.BlockCollection()
    fp = open(filename, "rb")
    blockCollection.ParseFromString(fp.read())
    fp.close()
    return blockCollection

def listBlocksInCollection(blocks):
    for blk in blocks:
        print blk.getDecimalIndex()

def blockCollectionDisk2BlockObject(blockCollection):
    b = []
    bSize = blockCollection.blockBitSize
    for i in blockCollection.collection:
        bObj = Block(0,bSize, True)
        bObj.buildBlockFromProtoBufDisk(i.blk)
        b.append(bObj)
    return b

def blockCollection2BlockObject(blockCollection):
    b = []
    bSize = blockCollection.blockBitSize
    for blk in blockCollection.blocks:
        bObj = Block(0,0)
        bObj.buildBlockFromProtoBuf(blk.index, blk.data, bSize) 
        b.append(bObj)
    return b


def main():

    p = argparse.ArgumentParser(description='BlockEngine Driver')

    p.add_argument('-n', dest='numBlocks', action='store', type=int,
                   default=2, help='Number of blocks to create')
    
    p.add_argument('-s', dest='dataSize', action='store', type=int,
                   default=64, help='Block data size')
    
    p.add_argument('-w', dest='fpW', action='store', default=None,
                   help='File to write Block collection')

    p.add_argument('-r', dest='fpR', action='store', default=None,
                   help='File to read Block collection')


    args = p.parse_args()
    
            
    if args.fpW == None and args.fpR == None:
        print "Please specfiy a read or write operation"
        sys.exit(1)
    
    if args.fpW != None:
        
        if args.numBlocks <= 0:
            print "Please specify a number of blocks > 0"
            sys.exit(1)

        if args.dataSize <= 0:
            print "Please specify data blocks size > 0"
            sys.exit(1)

        start = datetime.datetime.now()
        blocks = createBlocks(args.numBlocks, args.dataSize)
        #blkCol = createBlockProtoBufs(blocks, args.dataSize)
        blkCol = createBlockProtoBufsDisk(blocks, args.dataSize)
        writeBlockCollectionToFile(args.fpW, blkCol)
        end = datetime.datetime.now()
        
        print "Time passed Creating/Writing: ", end-start
        
        if TEST:
            start = datetime.datetime.now()
            #blkCol = readBlockCollectionFromFile(args.fpW)
            blkCol = readBlockCollectionFromDisk(args.fpW)
            blocks = blockCollectionDisk2BlockObject(blkCol)
            listBlocksInCollection(blocks)
            end = datetime.datetime.now()
            print "Time passed Reading: ", end-start
            
    if args.fpR:
        start = datetime.datetime.now()
        blkCol = readBlockCollectionFromFile(args.fpR)
        listBlocksInCollection(blkCol)
        end = datetime.datetime.now()
        

if __name__ == "__main__":
    main()
        