from Crypto.Util import number

class TagGenerator(object):
    '''
    Class to generate tags from blocks
    '''


    def __init__(self, hashFunctionObject):
        self.h = hashFunctionObject
    
    def getW(self, blocks, u):
        w_collection = []
        for blk in blocks:
            index = blk.getStringIndex()
            wBlk = index + str(u)
            w_collection.append(wBlk)
        return w_collection

    def getTags(self, w_collection, g, blocks, d, n):
        tags = []
        for (w, b) in zip(w_collection, blocks):
            bLong =  number.bytes_to_long(b.data.tobytes())
            powG = pow(g,bLong, n)
            self.h.update(str(w))
            wHash = number.bytes_to_long(self.h.digest())
            wGmodN = pow((wHash*powG),1, n)
            res = pow(wGmodN, d, n)
            tags.append(res)
        return tags
        