'''
Created on 2013-01-31

@author: fejes
'''
import unittest
import ReadAheadIteratorPET




class FakeAlignedRead():
    
    def __init__(self, aend, alen, rev):
        self.aend = aend
        self.alen = alen        
        self.is_reverse = rev  


class Test(unittest.TestCase):

    def testReadAhead(self):
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET("../testdata/ex1.sam", 200, "r", True)
        count = 0
        while readahead.isValid():
            alignedreadobjpet = readahead.getNext()
            if alignedreadobjpet == None:
                break
            count +=1
        print "read", count, "objects"
        self.assertEqual(count, 1572)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()