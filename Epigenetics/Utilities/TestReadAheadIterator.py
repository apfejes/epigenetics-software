'''
Created on 2013-01-31

@author: fejes
'''
import unittest
import ReadAheadIterator




class FakeAlignedRead():
    
    def __init__(self, pos, alen, rev):
        self.pos = pos
        self.alen = alen        
        self.is_reverse = rev  


class Test(unittest.TestCase):

    def testReadAhead(self):
        readahead = ReadAheadIterator.ReadAheadIterator("/home/afejes/workspacePython/data/ex1.sam", 200, "r")
        count = 0
        while readahead.isValid():
#            alignedreadobj = readahead.getNext()
            readahead.getNext()
            if readahead.isReadValid == False:
                break
            count +=1
        ''' print alignedreadobj '''
        print "read", count, "objects"


    def testProcessReads(self):
        '''a = FakeAlignedRead(100, 125, FakeAlignedRead(10,25,True))
        b = FakeAlignedRead(120, 145, FakeAlignedRead(10,25,False))
        c = FakeAlignedRead(110, 175, FakeAlignedRead(10,25,True))
        d = FakeAlignedRead(100, 165, FakeAlignedRead(10,25,False))'''
        pass
        
        
    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()