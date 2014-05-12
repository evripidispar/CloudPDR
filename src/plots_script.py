import numpy as np
import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt


def readStatsFromFile(filename, numdiffplots):
    statsFile = open(filename, "r")
    
    times_set={}
    numBlocks_list=[]
    for line in statsFile:
        index = 0
        values = line.split()
        numBlocks_list.append(values[0])
        while (index < numdiffplots):
            if index not in times_set.keys():
                times_set[index]= []
            times_set[index].append(float(values[index+1]))
            index+=1
    
    statsFile.close()
    
    return (times_set, numBlocks_list)
                  
    
def plotlines(filename, numdiffplots, labels, filename_output, xlabel='', ylabel='', title=''):
    colors = ['r','g','b']
    markers = ['x','.','+']
    index = 0
    plt.figure(1)
    times_set, numBlocks_list = readStatsFromFile (filename, numdiffplots)
    plt.axis([0, 6, 0, 20])
    while (index < len(times_set)):
        line, = plt.plot(numBlocks_list, times_set[index], label = labels[index])
        line.set_antialiased(False) # turn off antialising
        plt.setp(line, color = colors[index], marker = markers[index], markeredgewidth = 2.0)
        index+=1
  
    plt.legend()
    plt.xlabel(xlabel)    
    plt.ylabel(ylabel)
    plt.title(title)
    #plt.show()
    plt.savefig(filename_output)
        
def plotbar(filename, numdiffplots, labels, filename_output,xlabel='', ylabel='', title=''):
    colors = ['r','g','b']
    markers = ['x','.','+']
    index = 0
    plt.figure(2)
    times_set, numBlocks_list = readStatsFromFile (filename, numdiffplots)
    ind = np.arange(len(numBlocks_list))    # the x locations for the groups
    width = 0.25       # the width of the bars: can also be len(x) sequence
    bottom = np.array([0.0] * len(times_set[index]))
    while (index<len(times_set)):
        if index == 0:
            p = plt.bar(ind, times_set[index], width, color = colors[index], label = labels[index])
        else:
            bottom = bottom + times_set[index-1]
            p = plt.bar(ind, times_set[index], width, bottom, color = colors[index], label = labels[index])  
        index+=1
  
    plt.xlabel(xlabel)    
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(ind+width/2., numBlocks_list )
    #plt.yticks(np.arange(0,81,10))
    plt.legend()
    #plt.show()  
    plt.savefig(filename_output)
     
plotlines("./test.dat", 3, ['first','second','third'],'../plots/test_output_plot','numblocks','times','Output')

plotbar("./test.dat", 3 ,['first','second','third'],'../plots/test_output_bar','numblocks','times','Output')
