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
        #print "read", count, "objects"
        self.assertEqual(count, 1572)

    def testPushBack(self):
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET("../testdata/ex1.sam", 200, "r", True)
        count = 0
        array_of_reads = []
        for dummy in range(0,10):
            alignedreadobjpet = readahead.getNext()
            array_of_reads.append(alignedreadobjpet)
        readahead.pushback(array_of_reads)
        
        last_read_start=-1000000;  #a useless start point, we can be sure reads won't be mapped that far upstream
        while readahead.isValid():
            alignedreadobjpet = readahead.getNext()
            self.assert_(last_read_start <= alignedreadobjpet.left_end, "reads passed out of order!")
            if alignedreadobjpet == None:
                break
            last_read_start = alignedreadobjpet.left_end
            count +=1
            
            
        #print "read", count, "objects"
        self.assertEqual(count, 1572)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()