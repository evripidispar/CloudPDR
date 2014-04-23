import argparse
import sys
from BlockUtil import *
from Ibf import *
from CloudPDRObj import *


def main():
    p = argparse.ArgumentParser(description='Driver for IBF')

    p.add_argument('--num', dest='numBlocks', action='store', type=int,
                   default=2, help='Number of blocks in IBF')

    p.add_argument('--common', dest='numCommon', action='store', type=int,
                   default=2, help='Common blocks in IBF')

    p.add_argument('--size', dest='dataSize', action='store', type=int,
                   default=512, help='Block data size')

    p.add_argument('--total', dest='totalBlocks', action='store', type=int,
                   default=200, help='Number of blocks to create')

    
    p.add_argument('-m', dest='ibfLen', action='store', type=int,
                   default=500, help='Length of the bloom filter')
    
    p.add_argument('-k', dest='hashNum', action='store', type=int,
                   default=5, help='Number of hash arguments')

    args = p.parse_args()

    if args.numBlocks <= 0:
        print "Number of blocks should be positive"
        sys.exit(1)

    if args.numCommon <= 0:
        print "Number of common should be positive"

    if args.numCommon > args.numBlocks:
        print  "NumCommon less than equal of numBlocks"
        sys.exit(1)
    if args.dataSize <= 0:
        print "Data size should positive"
        sys.exit(1)

    if args.totalBlocks < 2 * args.numBlocks:
        print "Total blocks should be bigger then numBlocks"
        sys.exit(1)
    
    if args.hashNum > 10: 
        print "Number of hashFunctions should be less than 10"
        sys.exit(1)
        
    
    blocks = blockCreatorMemory(args.totalBlocks, args.dataSize)
    commonBlocks = pickCommonBlocks(args.numBlocks, args.numCommon)
    diff_a, diff_b = pickDiffBlocks(args.numBlocks, commonBlocks, args.totalBlocks)

    cObj = CloudPDRObj(1024, "generator.txt")

    ibfA = Ibf(4, 1000)
    ibfB = Ibf(4, 1000)

    for cBlock in commonBlocks:
        ibfA.insert(blocks[cBlock], cObj.secret, cObj.N, cObj.g, args.dataSize)
        ibfB.insert(blocks[cBlock], cObj.secret, cObj.N, cObj.g, args.dataSize)

    for diffBlock in diff_a:
        ibfA.insert(blocks[diffBlock], cObj.secret, cObj.N, cObj.g, args.dataSize)

    for diffBlock in diff_b:
        ibfB.insert(blocks[diffBlock], cObj.secret, cObj.N, cObj.g,  args.dataSize)

    
    pureCellsA = ibfA.getPureCells()
    pureCellsB = ibfB.getPureCells()
    
    print "len of pureCells in A: ", len(pureCellsA)
    print "len of pureCells in B: ", len(pureCellsB)
    
    
    for i in commonBlocks:
        s = ibfA.findBlock(blocks[i])
        print "Block: ", i, "Found", s
    
    for i in commonBlocks:
        ibfA.delete(blocks[i], cObj.secret, cObj.N, cObj.g)
    
    print "-------"
    
    for i in commonBlocks:
        s = ibfA.findBlock(blocks[i])
        print "Block: ", i, "Found", s
    
    
    
    


if __name__ == "__main__":
    main()