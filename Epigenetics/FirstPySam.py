import array
from Utilities import ReadAheadIterator 

fragmentLength = 250




def makeIslands(start, end):
    #map = array('I')
    map_i = array.array('i',(0 for i in range(0,end-start)))
    print(map_i[0])


# Once a file is opened you can iterate over all of the read mapping to a specified region using fetch(). Each iteration returns a AlignedRead object which represents a single read along with its fields and optional tags:


#do something with input

readahead = ReadAheadIterator.ReadAheadIterator("testdata/ChipSeqGSE31221/GSE31221_RAW/GSM773994_TCF7_ChIPSeq.bam", fragmentLength, "rb")
while True:
    alignedreadobj = readahead.getNext()
    alignedreadobj.type()
    alignedread = alignedreadobj.get_read()
    print "1"
    if not readahead.isReadValid:
        break
    #print alignedread
    print alignedread.tid, readahead.get_ref_name(alignedread.tid), alignedread.pos, alignedread.alen, alignedread.is_reverse, alignedread.is_paired, alignedread.is_proper_pair
    

 

readahead.close()
