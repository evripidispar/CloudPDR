import Block

class Cell(object):

    def __init__(self):
        self.count = 0
        self.dataSum = 0
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

    def produceHashProdAdd(self, block):
        return 0

    def produceHashProdRmv(self, block):
        return 0

    def add(self, block) :
        self.count += 1
        self.dataSum += self.getBlockData(block)  #TODO: add blocks how?
        self.hashProd = self.produceHashProdAdd(block)
        return

    def remove(self, block):

        #count handling
        if (self.count < 0):
            self.count +=1
        else:
            self.count -=1

        self.dataSum -= self.getBlockData(block) #TODO: subtract blocks how?
        self.hashProd = self.produceHashProdRmv(block)


    def isPure(self):
        if self.count == 1: #TODO:  is this correct?
            return True
        return False

    def isEmpty(self):
        if self.count == 0:
            return True
        return False

    def subtract(self, otherCell):
        diffCell = Cell()
        c  = self.count - otherCell.getCount()
        hp = self.modDivision(self.hashProd, otherCell.getHashProd)
        dS = self.dataSum - otherCell.getDataSum()

        diffCell.setCount(c)
        diffCell.setDataSum(ds)
        diffCell.setHashProd(hp)

        return diffCell


