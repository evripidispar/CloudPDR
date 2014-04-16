import Block
from CryptoUtil import number

class Cell(object):

    def __init__(self):
        self.count = 0
        self.dataSum = Block(0)
        self.hashProd = 0

    def setCount(count):
        self.count = count

    def setHashProd(hashProd):
        self.hashProd = hashProd

    def setDataSum(dataSum):
        self.dataSum = dataSum

    def getCount(self):
        return self.count

    def getHashProd(self):
        return self.hashProd

    def getDataSum(self):
        return self.dataSum


    def add(self, block, secret, N):
        self.count += 1
        self.dataSum.addBlockData(block)  
        f = generate_f(block, N, secret)
        self.hashProd *= self.produceHashProdAdd(block, secret) #TODO: not sure this is the write way to go 
        self.hashProd = pow(self.hashProd, 1, N)
        return

    def remove(self, block,  s):
        #TODO 
        #count handling
        if (self.count < 0):
            self.count +=1
        else:
            self.count -=1

        self.dataSum.addBlockData(block)
        f = generate_f(block, N, secret)
        fInv = number.inverse(f,N) #TODO: Not sure this is true
        self.hashProd *= fInv
        self.hashProd = pow(self.hashProd, 1, N)


    def isPure(self):
        if self.count == 1: #TODO:  is this correct?
            return True
        return False

    def isEmpty(self):
        if self.count == 0:
            return True
        return False

    def subtract(self, otherCell):
        #TODO
        diffCell = Cell()
        c  = self.count - otherCell.getCount()
        hp = self.modDivision(self.hashProd, otherCell.getHashProd) #TODO: modDivision
        dS = self.dataSum - otherCell.getDataSum() #TODO 

        diffCell.setCount(c)
        diffCell.setDataSum(ds)
        diffCell.setHashProd(hp)

        return diffCell


