'''
Created on 2013-01-31

@author: fejes
'''
import unittest
import os
import ReadAheadIteratorPET




class FakeAlignedRead():
    '''A simple class that can be used as a stand-in for an aligned read.'''

    def __init__(self, aend, alen, rev):
        '''init function - holds end, length, strand.'''
        self.aend = aend
        self.alen = alen
        self.is_reverse = rev


class Test(unittest.TestCase):
    '''Test class for testing readahead iterator'''

    def testReadAhead_onlyPet(self):
        '''testing with PET reads only'''
        path = os.path.dirname(os.path.abspath(__file__))
        path = path.rsplit("/", 2)
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(path[0] + "/testdata/ex1.sam", 200, "r", False)
        count = 0
        chr_count = 0
        current_chromosome = None

        while readahead.isValid():    # test if the reads are still good.

            alignedreadobjpet = readahead.getNext()
            if alignedreadobjpet is None:
                # move to next chromosome
                chr_count = 0
                print "returned a None!"
                continue
            alignedread1 = alignedreadobjpet.read1
            chromosome = readahead.get_ref_name(alignedread1.tid)
            if current_chromosome != chromosome:
                if current_chromosome != None:
                    print "chromosome", current_chromosome, "had", count, "reads"
                current_chromosome = chromosome
                chr_count = 0
            chr_count += 1
            count += 1
            # print "gets = ", readahead.gets
        # print "read", count, "objects"
        print "chromosome", current_chromosome, "had", chr_count, "reads"
        print "gets", readahead.gets
        self.assertEqual(count, 1699)

    def testReadAhead_allReads(self):
        '''Test with PET and SET'''
        path = os.path.dirname(os.path.abspath(__file__))
        path = path.rsplit("/", 2)
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(path[0] + "/testdata/ex1.sam", 200, "r", False)
        count = 0
        while readahead.isValid():
            alignedreadobjpet = readahead.getNext()
            if alignedreadobjpet is None:
                break
            count += 1
        # print "read", count, "objects"
        self.assertEqual(count, 1699)


    def testPushBack(self):
        '''Test the pushback function of the iterator'''
        path = os.path.dirname(os.path.abspath(__file__))
        path = path.rsplit("/", 2)
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(path[0] + "/testdata/ex1.sam", 200, "r", True)
        count = 0
        array_of_reads = []
        current_chromosome = None
        for dummy in range(0, 10):
            alignedreadobjpet = readahead.getNext()
            array_of_reads.append(alignedreadobjpet)
        readahead.pushback(array_of_reads)

        last_read_start = -1000000    # a useless start point, we can be sure reads won't be mapped that far upstream
        while readahead.isValid():
            alignedreadobjpet = readahead.getNext()
            alignedread1 = alignedreadobjpet.read1
            chromosome = readahead.get_ref_name(alignedread1.tid)
            if current_chromosome != chromosome:
                last_read_start = -1000000
                current_chromosome = chromosome
            else:
                self.assert_(last_read_start <= alignedreadobjpet.left_end, "reads passed out of order!")
            if alignedreadobjpet is None:
                break
            last_read_start = alignedreadobjpet.left_end
            count += 1
        # print "read", count, "objects"
        self.assertEqual(count, 1699)



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
