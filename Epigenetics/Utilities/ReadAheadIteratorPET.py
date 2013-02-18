'''
Created on 2013-01-28

@author: fejes
'''
import pysam
import AlignedReadObjPET
import DoublyLinkedList


class ReadAheadIteratorPET():
    
    
    '''create variables used by the readahead iterator.'''
    buffer_reads = DoublyLinkedList.DLL()
    MaxReadAhead = 5000
    reads_processed = dict()
    only_PET_reads = True
    
    
    def type(self):
        print ("ReadAheadIteratorPET")
    
    '''initialize the readahead iterator with the parameters it requires'''
    def __init__(self, filename, fragmentLength, flags, only_PET):
        self.samfile = pysam.Samfile(filename, flags)
        self.iterator = self.samfile.__iter__()
        self.isReadValid = True
        self.fragmentLength = fragmentLength
        only_PET_reads = only_PET
        return

    '''private version of next - should not be used by external next calls'''
    def _next(self):
        try:
            while (True):  # may only break out by hitting end of file or by finding a pair.
                a = self.iterator.next()   # try to get the next element
                while a.is_unmapped:       #ignore reads that are unmapped
                    a = self.iterator.next()
                if ReadAheadIteratorPET.reads_processed.has_key(a.qname):
                    a2 = ReadAheadIteratorPET.reads_processed.pop(a.qname)
                    if ReadAheadIteratorPET.reads_processed.has_key(a.qname):
                        print "key a.qname still found", a.qname
                    
                    return ReadAheadIteratorPET._apply_frag_properties(self, a, a2)
                else:
                    if (a.mate_is_unmapped):
                        if (ReadAheadIteratorPET.only_PET_reads):
                            continue
                        else:
                            return ReadAheadIteratorPET._apply_frag_properties(self, a, None)
                    else:
                        ReadAheadIteratorPET.reads_processed[a.qname] = a
            '''end while'''
        except StopIteration:           # can't retrieve next element
        #   print "Stop iteration hit -", self.buffer_reads.size(), "reads found in buffer"
        #    p = ReadAheadIteratorPET.buffer_reads.head
        #    while p!= None:
        #        print "buffer:", p.holding.read1, "and", p.holding.read2
        #        p = p.next
            self.isReadValid = False    # set warning flag that there are no more to retrieve
            return None                 # return an empty object
        return a                        # otherwise, return the good object found.

    '''private function for converting fragments to the proper read lengths'''
    def _apply_frag_properties(self, alignedread1, alignedread2):
        left_end= 0
        right_end = 0
        ''' print 'proper pairing:' + (" Yes" if alignedread1.is_proper_pair else " No") + (" Yes" if alignedread2.is_proper_pair else " No")'''
        if alignedread1.is_proper_pair and alignedread2.is_proper_pair:
            
            if alignedread1.is_reverse:
                e1 = alignedread1.pos - alignedread1.alen
            else:
                e1 = alignedread1.pos
            if alignedread2.is_reverse:            
                e2 = alignedread2.pos - alignedread2.alen
            else:
                e2 = alignedread2.pos
            left_end = (e1 if e1 <= e2 else e2)
            if alignedread1.is_reverse:
                e1 = alignedread1.pos
            else:
                e1 = alignedread1.pos + alignedread1.alen
            if alignedread2.is_reverse:
                e2 = alignedread2.pos
            else:
                e2 = alignedread2.pos + alignedread1.alen
            right_end = (e1 if e1 >= e2 else e2)
            '''print "position of the mates:", alignedread1.mpos, alignedread1.mpos''' 
            '''*********************************'''
        else:
            print "These reads are not properly paired!", alignedread1, alignedread2
        return AlignedReadObjPET.AlignedReadObjPET(left_end, right_end, alignedread1, alignedread2)
        
    '''read ahead, go as far as needed - pushes data into the buffer'''
    def read_ahead(self):
        first_read_start = ReadAheadIteratorPET.buffer_reads.head.holding.left_end
        last_read_start = ReadAheadIteratorPET.buffer_reads.tail.holding.left_end

        while self.isReadValid and first_read_start + ReadAheadIteratorPET.MaxReadAhead < last_read_start:
            read = self._next()
            if read == None:
                return None
            else:
                
                min_read = self._apply_frag_properties(read)
                if ReadAheadIteratorPET.buffer_reads.size() == 0:  #handles empty buffer.
                    last_read_start = min_read.left_end
                    first_read_start = min_read.left_end
                else:                                   #handles non-empty buffer.
                    if min_read.left_end < first_read_start:
                        first_read_start = min_read.left_end
                        ReadAheadIteratorPET.buffer_reads.insert_at_head(min_read)
                    elif min_read.left_end > last_read_start:
                        last_read_start = min_read.left_end
                        ReadAheadIteratorPET.buffer_reads.append(min_read)
                    else:   #read should be put in the buffer where it belongs.
                        '''traverse list backwards'''
                        p = ReadAheadIteratorPET.buffer_reads.tail
                        while not p == None: 
                            if read.left_end >= p.holding.left_end:
                                ReadAheadIteratorPET.buffer_reads.insert_after(p, read)
                                break
                            p = p.next
        return None
        
    '''private function for populating the buffer and reading ahead.'''
    def populate_buffer(self):
        if ReadAheadIteratorPET.buffer_reads.size() > 0: 
            first_start = ReadAheadIteratorPET.buffer_reads.head.holding.left_end
            last_start = ReadAheadIteratorPET.buffer_reads.tail.holding.left_end
        else:
            first_start = -1
            last_start = -1
        while (self.isReadValid and ((last_start == -1) or (first_start + ReadAheadIteratorPET.MaxReadAhead < last_start))):
            read = self._next()  # returns min_read
            if read == None:
                return None            
            else:
                '''print read.get_left_end(), read.get_right_end(), read.get_read1(), read.get_read2()'''
                self._insert_into_buffer(read)
        return None

    def _insert_into_buffer(self, read):
        if (self.buffer_reads.size() == 0):
            self.buffer_reads.append(read)
        else:
            p = self.buffer_reads.tail
            while not p == None:
                if p.holding.left_end < read.left_end:
                    self.buffer_reads.insert_after(p, read)
                    return None
                p = p.prev
            else:
                self.buffer_reads.insert_at_head(read)

    '''function to get next - to be used externally to access the buffer'''
    def getNext(self):
        if ReadAheadIteratorPET.buffer_reads.size() == 0 and not self.isReadValid:
            return None
        else:
            if self.isReadValid:
                self.populate_buffer()
            return ReadAheadIteratorPET.buffer_reads.pop_head()        
        
        
    '''use this function to close the file after reading is complete'''
    def close(self):
        self.samfile.close()
        return None


    '''function to be used to test if the current read is valid.'''
    def isValid(self):
        if ReadAheadIteratorPET.buffer_reads.size() > 0:
            return True
        else:
            return self.isReadValid
