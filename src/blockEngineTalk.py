import argparse
from os import system
from sys import exit
def main():

    blockSizes = [512, 1024, 2048, 4096, 8192, 16384, 32768]
    blockNumbers = [100, 1000, 10000, 100000, 500000]
    
    desc = "BlockEngineTalk: orders BlockEngine.py to create files \n"
    desc += "of different block sizes and different number of blocks"
    p = argparse.ArgumentParser(description=desc)
    
    p.add_argument('--maxNum', dest="maxBlock", action="store", type=int,
                   default=max(blockNumbers), help="Max number of blocks in a file")
    
    p.add_argument('--maxSize', dest="maxSize", action="store", type=int,
                   default=max(blockSizes), help="Max block size in KB")
    
    
    args = p.parse_args()
 
    if args.maxSize > max(blockSizes):
        print "Block size cannot be larger than", max(blockSizes)
        exit(-1)
    
    if args.maxSize < min(blockSizes):
        print "Block size cannot be less than", min(blockSizes)
        exit(-1)
        
    if args.maxBlock > max(blockNumbers):
        print "Block number cannot be larger than ", max(blockNumbers)
        exit(-1)
    
    if args.maxBlock < min(blockNumbers):
        print "Block number cannot be less than ", min(blockNumbers)
        exit(-1)
    
    
    for bNum in blockNumbers:
        if bNum > args.maxBlock:
            continue
        
        for bSize in blockSizes:
            if bSize > args.maxSize:
                continue
            
            fName = "blocks/blk_%d_blocks_%d_sizeBytes.dat" % (bNum, bSize)
            cmd = "python BlockEngine.py -n %d -s %d -w %s" %(bNum, bSize, fName)
            print "Creating file", fName
            system(cmd)
            print "# # # # # # # # # # # "
            
if __name__ == "__main__":
    main()

