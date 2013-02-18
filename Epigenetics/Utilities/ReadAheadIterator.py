'''
Created on 2013-01-28

@author: fejes
'''
import pysam
import AlignedReadObj
import DoublyLinkedList


class ReadAheadIterator():
    
    
    '''create variables used by the readahead iterator.'''
    buffer_reads = DoublyLinkedList.DLL()
    MaxReadAhead = 5000
    
    def type(self):
        print ("ReadAheadIterator")
    
    '''initialize the readahead iterator with the parameters it requires'''
    def __init__(self, filename, fragmentLength, flags):
        self.samfile = pysam.Samfile(filename, flags)
        self.iterator = self.samfile.__iter__()
        self.isReadValid = True
        self.fragmentLength = fragmentLength
        return

    '''private version of next - should not be used by external next calls'''
    def _next(self):
        try: 
            a = self.iterator.next()   # try to get the next element
            while a.is_unmapped:       #ignore reads that are unmapped
                a = self.iterator.next()
        except StopIteration:           # can't retrieve next element
            self.isReadValid = False    # set warning flag that there are no more to retrieve
            return None                 # return an empty object
        return a                        # otherwise, return the good object found.

    '''private function for converting fragments to the proper read lengths'''
    def _apply_frag_properties(self, alignedread):
        left_end= 0
        right_end = 0
        if alignedread.is_reverse:
            right_end = alignedread.pos + alignedread.alen
            left_end = right_end - self.fragmentLength
        else:
            left_end = alignedread.pos
            right_end = left_end + self.fragmentLength
        ''' print left_end, right_end, alignedread.pos, (alignedread.pos +alignedread.alen), ("Reverse" if alignedread.is_reverse else "Forward")'''
        return AlignedReadObj.AlignedReadObj(left_end, right_end, alignedread)
        
    '''read ahead, go as far as needed - pushes data into the buffer'''
    def read_ahead(self):
        first_read_start = ReadAheadIterator.buffer_reads.head.holding.left_end
        last_read_start = ReadAheadIterator.buffer_reads.tail.holding.left_end

        while self.isReadValid and (first_read_start + ReadAheadIterator.MaxReadAhead < last_read_start):
            read = self._next()
            if read == None:
                return None
            else:
                
                min_read = self._apply_frag_properties(read)
                if ReadAheadIterator.buffer_reads.size() == 0:  #handles empty buffer.
                    last_read_start = min_read.left_end
                    first_read_start = min_read.left_end
                else:                                   #handles non-empty buffer.
                    if min_read.left_end < first_read_start:
                        first_read_start = min_read.left_end
                        ReadAheadIterator.buffer_reads.insert_at_head(min_read)
                    elif min_read.left_end > last_read_start:
                        last_read_start = min_read.left_end
                        ReadAheadIterator.buffer_reads.append(min_read)
                    else:   #read should be put in the buffer where it belongs.
                        '''traverse list backwards'''
                        p = ReadAheadIterator.buffer_reads.tail
                        while not p == None: 
                            if read.left_end >= p.holding.left_end:
                                ReadAheadIterator.buffer_reads.insert_after(p, read)
                                break
                            p = p.next
        return None
        
    '''private function for populating the buffer and reading ahead.'''
    def populate_buffer(self):
        # last and #first
        if ReadAheadIterator.buffer_reads.size() > 0: 
            first_start = ReadAheadIterator.buffer_reads.head.holding.left_end
            last_start = ReadAheadIterator.buffer_reads.tail.holding.left_end
        else:
            first_start = -1
            last_start = -1

        print "before:", first_start + ReadAheadIterator.MaxReadAhead,">", last_start
        while (self.isReadValid and ((first_start == -1) or (first_start + ReadAheadIterator.MaxReadAhead > last_start))):

            read = self._next()
            if read == None:
                return None
            else:
                min_read = self._apply_frag_properties(read)
                if first_start == -1:
                    first_start = min_read.left_end
                last_start = min_read.left_end
                '''print min_read.get_left_end(), min_read.get_right_end(), min_read.get_read()'''
                self._insert_into_buffer(min_read)
            print "After:", first_start + ReadAheadIterator.MaxReadAhead,">", last_start
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
        if ReadAheadIterator.buffer_reads.size() == 0 and not self.isReadValid:
            return None
        else:
            self.populate_buffer()
            return ReadAheadIterator.buffer_reads.pop_head()        
        
        
    '''use this function to close the file after reading is complete'''
    def close(self):
        self.samfile.close()
        return None


    '''function to be used to test if the current read is valid.'''
    def isValid(self):
        return self.isReadValid
    
    def get_ref_name(self, tid):
        return self.samfile.getrname(tid)
