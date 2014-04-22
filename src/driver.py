import argparse
import sys
from BlockUtil import *
from Ibf import *
from CloudPDRObj import *


def main():
    p = argparse.ArgumentParser(description='Driver for IBF')

    p.add_argument('--num', dest='numBlocks', action='store',
                   default=100, help='Number of blocks in IBF')

    p.add_argument('--common', dest='numCommon', action='store',
                   default=50, help='Common blocks in IBF')

    p.add_argument('--size', dest='dataSize', action='store',
                   default=512, help='Block data size')

    p.add_argument('--total', dest='totalBlocks', action='store',
                   default=200, help='Number of blocks to create')

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

    
    blocks = blockCreatorMemory(args.totalBlocks, args.dataSize)
    commonBlocks = pickCommonBlocks(args.numBlocks, args.numCommon)
    diff_a, diff_b = pickDiffBlocks(args.numBlocks, commonBlocks, args.totalBlocks)

    cObj = CloudPDRObj(1024)

    ibfA = Ibf(5, 500)
    ibfB = Ibf(5, 500)

    for cBlock in commonBlocks:
        print cBlock
        ibfA.insert(blocks[cBlock], cObj.secret, cObj.N)
        ibfB.insert(blocks[cBlock], cObj.secret, cObj.N)

    for diffBlock in diff_a:
        ibfA.insert(blocks[diffBlock], cObj.secret, cObj.N)

    for diffBlock in diff_b:
        ibfB.insert(blocks[diffBlock], cObj.secret, cObj.N)


if __name__ == "__main__":
    main()