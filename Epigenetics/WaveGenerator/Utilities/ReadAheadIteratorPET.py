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
    reserve_read = None
    MaxReadAhead = 5000
    reads_processed = dict()
    only_PET_reads = False
    current_chromosome = None

    @staticmethod
    def type():
        '''print ReadAheadIteratorPET, identify the class'''
        print ("ReadAheadIteratorPET")

    def __init__(self, filename, fragment_length, flags, only_PET):
        '''initialize the readahead iterator with the parameters it requires'''
        self.samfile = pysam.Samfile(filename, flags)    # @UndefinedVariable
        self.iterator = self.samfile.__iter__()
        self.isReadValid = True
        self.fragmentLength = fragment_length
        self.only_PET_reads = only_PET
        self.gets = 0
        # print "self.only_PET_reads", self.only_PET_reads
        return


    def _next(self):
        '''private version of next - should not be used by external next calls'''
        try:
            while (True):    # may only break out by hitting end of file or by finding a pair.
                a = self.iterator.next()    # try to get the next element
                self.gets += 1
                while a.is_unmapped:    # ignore reads that are unmapped
                    # self.unmapped_reads += 1
                    a = self.iterator.next()
                    if a is None:
                        return None
                if a.is_paired:    # if it's a PET read
                    if ReadAheadIteratorPET.reads_processed.has_key(a.qname):    # have you seen the other pair?
                        a2 = ReadAheadIteratorPET.reads_processed.pop(a.qname)
                        # if ReadAheadIteratorPET.reads_processed.has_key(a.qname):
                        #    print "key a.qname still found", a.qname
                        # self.paired_reads += 2
                        return ReadAheadIteratorPET._apply_frag_properties(self, a, a2)

                    else:    # if you haven't seen the other pair
                        if a.mate_is_unmapped:    # if it's pair isn't mappped,
                            if (ReadAheadIteratorPET.only_PET_reads):    # don't keep it if you only want Paired reads
                                continue
                            else:    # otherwise, keep if and process it if you want SET reads too.
                                return ReadAheadIteratorPET._apply_frag_properties(self, a, None)
                        else:    # mate is mapped, but you haven't seen it, put it into the processed reads bin
                            ReadAheadIteratorPET.reads_processed[a.qname] = a
                else:    # single end read.
                    if not ReadAheadIteratorPET.only_PET_reads:
                        return ReadAheadIteratorPET._apply_frag_properties(self, a, None)
                    else:
                        continue
            # end while
        except StopIteration:    # can't retrieve next element
        #   print "Stop iteration hit -", self.buffer_reads.size(), "reads found in buffer"
        #    p = ReadAheadIteratorPET.buffer_reads.head
        #    while p!= None:
        #        print "buffer:", p.holding.read1, "and", p.holding.read2
        #        p = p.next
            self.isReadValid = False    # set warning flag that there are no more to retrieve
            return None    # return an empty object
        return a    # otherwise, return the good object found.


    def _apply_frag_properties(self, alignedread1, alignedread2):
        '''private function for converting fragments to the proper read lengths'''
        left_end = 0
        right_end = 0
        # print 'proper pairing:' + (" Yes" if alignedread1.is_proper_pair else " No") + (" Yes" if alignedread2.is_proper_pair else " No")'''
        # handling unpaired
        if alignedread2 is None:
            if alignedread1.is_reverse:
                left_end = alignedread1.pos - self.fragmentLength
            else:
                left_end = alignedread1.pos
            if alignedread1.is_reverse:
                right_end = alignedread1.pos
            else:
                right_end = alignedread1.pos + self.fragmentLength
        # Handling PET below
        elif (alignedread1.is_proper_pair and alignedread2.is_proper_pair):
            if alignedread1.is_reverse:
                e1 = alignedread1.pos - self.fragmentLength
            else:
                e1 = alignedread1.pos
            if alignedread2.is_reverse:
                e2 = alignedread2.pos - self.fragmentLength
            else:
                e2 = alignedread2.pos
            left_end = (e1 if e1 <= e2 else e2)
            if alignedread1.is_reverse:
                e1 = alignedread1.pos
            else:
                e1 = alignedread1.pos + self.fragmentLength
            if alignedread2.is_reverse:
                e2 = alignedread2.pos
            else:
                e2 = alignedread2.pos + self.fragmentLength
            right_end = (e1 if e1 >= e2 else e2)
            # print "position of the mates:", alignedread1.mpos, alignedread1.mpos
            #*********************************
        else:
            print "These reads are not properly paired!", alignedread1, alignedread2
        return AlignedReadObjPET.AlignedReadObjPET(alignedread1.tid, left_end, right_end, alignedread1, alignedread2)


    def read_ahead(self):
        '''read ahead, go as far as needed - pushes data into the buffer'''
        if (self.reserve_read != None):    # break when there is already a read in the reserve.  don't read ahead.
            return None
        if ReadAheadIteratorPET.buffer_reads.size() > 0:
            first_read_start = ReadAheadIteratorPET.buffer_reads.head.holding.left_end
            last_read_start = ReadAheadIteratorPET.buffer_reads.tail.holding.left_end
        else:
            first_read_start = -1
            last_read_start = -1

        while self.isReadValid and first_read_start + ReadAheadIteratorPET.MaxReadAhead > last_read_start and self.reserve_read is None:

            read = self._next()
            if read is None:
                return None
            else:
                if self.current_chromosome is None:
                    self.current_chromosome = read.chromosome_id
                else:
                    if self.current_chromosome != read.chromosome_id:
                        self.reserve_read = read
                        return None
                if ReadAheadIteratorPET.buffer_reads.size() == 0:    # handles empty buffer.
                    ReadAheadIteratorPET.buffer_reads.insert_at_head(read)
                    first_read_start = read.left_end
                    last_read_start = read.left_end
                elif read.left_end < first_read_start:
                    first_read_start = read.left_end
                    ReadAheadIteratorPET.buffer_reads.insert_at_head(read)
                    # print "added at head"
                elif read.left_end > last_read_start:
                    last_read_start = read.left_end
                    ReadAheadIteratorPET.buffer_reads.append(read)
                    # print "added at tail"
                else:    # read should be put in the buffer where it belongs.
                    '''traverse list backwards'''
                    p = ReadAheadIteratorPET.buffer_reads.tail
                    added = False
                    while p != None:
                        if read.left_end >= p.holding.left_end:
                            ReadAheadIteratorPET.buffer_reads.insert_after(p, read)
                            added = True
                            # print "added from tail"
                            break
                        p = p.prev
                    if not added:
                        print "Read was not added to buffer!!!!!!!"
        return None

    def getNext(self):
        '''function to get next - to be used externally to access the buffer'''
        if ReadAheadIteratorPET.buffer_reads.size() == 0 and not self.isReadValid:
            # End of file.
            return None
        elif ReadAheadIteratorPET.buffer_reads.size() == 0 and self.isReadValid:
            # end of chromosome - move to next
            if self.reserve_read != None:    # there is a read from the next chromosome waiting
                self.current_chromosome = self.reserve_read.chromosome_id
                if (self.reserve_read.read1.is_paired and not self.reserve_read.read1.mate_is_unmapped):
                    ReadAheadIteratorPET.reads_processed[self.reserve_read.read1.qname] = self.reserve_read.read1
                else:
                    ReadAheadIteratorPET.buffer_reads.append(self.reserve_read)    # move it to the buffer
                self.reserve_read = None
            # regardless, keep processing:
            self.read_ahead()    # populate the buffer.
            # print "popping read from buffer of size", ReadAheadIteratorPET.buffer_reads.size()
            return ReadAheadIteratorPET.buffer_reads.pop_head()
        else:
            if self.isReadValid:    # buffer has reads, but not end of file
                self.read_ahead()
            # print "buffer now contains", ReadAheadIteratorPET.buffer_reads.size(), "reads"
            return ReadAheadIteratorPET.buffer_reads.pop_head()


    def close(self):
        '''use this function to close the file after reading is complete'''
        self.samfile.close()
        return None



    def isValid(self):
        '''function to be used to test if the current read is valid.'''
        if ReadAheadIteratorPET.buffer_reads.size() > 0 or ReadAheadIteratorPET.reserve_read != None:
            return True
        else:
            return self.isReadValid

    @classmethod
    def pushback(cls, reads):
        '''Use this function to push read(s) back into the buffer, if you've read too far'''
        if isinstance(reads, AlignedReadObjPET.AlignedReadObjPET):
            ReadAheadIteratorPET.buffer_reads.insert_at_head(reads)
        else:    # if list of reads
            for min_read in reversed(reads):
                ReadAheadIteratorPET.buffer_reads.insert_at_head(min_read)


    def get_ref_name(self, tid):
        '''Return reference name'''
        return self.samfile.getrname(tid)
