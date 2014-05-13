import argparse
import os
import sys

def rewriteNames(filename):
    return 'blocks/'+filename

def getRunInfo(name):
    name = name.split("_")
    return (name[1], name[3])


def main():

    p = argparse.ArgumentParser(description='Experiment driver')
    
    p.add_argument('-b', dest='blkDir', action='store', default=None,
                   help='Filesystem directory')
    
    p.add_argument('-r', dest='runsPerFs', action='store', type=int,
                   default=5, help='Number of runs Per Filesystem')
    

    p.add_argument('-o', dest='outDir', action='store', help='OutputDirectory')

    args = p.parse_args()
    availableFS = os.listdir(args.blkDir)
    fsFiles = map(rewriteNames, availableFS)
    
    task = 100
    w = 4
    k = 5
    
    print "#!/bin/bash"
    for fName,runId in zip(fsFiles,availableFS):
        for r in xrange(args.runsPerFs):
            blocks, size = getRunInfo(fName)
            runName = "runs/"+blocks+"__"+"__"+size+".txt"
            cmd = "python driver.py -b %s -g generator.txt -k %d -n 1024 -w %d --task %d -r %s ;" % (fName, k, w, task, runName)
#             os.system(cmd)
            print cmd
        sys.exit(1)  
    

if __name__ == "__main__":
    main()