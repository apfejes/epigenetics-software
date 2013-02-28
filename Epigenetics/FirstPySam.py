import array
from Utilities import ReadAheadIteratorPET 

fragmentLength = 250

def makeIslands(start, end):
    #map = array('I')
    map_i = array.array('i',(0 for i in range(0,end-start)))
    print(map_i[0])


# Once a file is opened you can iterate over all of the read mapping to a specified region using fetch(). Each iteration returns a AlignedRead object which represents a single read along with its fields and optional tags:


#do something with input

readahead = ReadAheadIteratorPET.ReadAheadIteratorPET("testdata/ChipSeqGSE31221/GSE31221_RAW/18_19_GSM773994_TCF7_ChIPSeq.bam", fragmentLength, "rb", False)
current_chromosome = None
count = 0;
while True:
    #print count, "reads processed"
    alignedreadobjpet = readahead.getNext()
    if not readahead.isReadValid:
        break
    
    #print alignedreadobjpet.type()
    
    if (alignedreadobjpet == None) :
        #flush chromosomome related objects, then continue
        continue
    
    alignedread = alignedreadobjpet.get_read1()
    chromosome = readahead.get_ref_name(alignedread.tid)
    
    if current_chromosome != chromosome:
        if current_chromosome != None:
            print "chromosome", current_chromosome, "had", count, "reads"

        current_chromosome = chromosome
        count= 0
    count +=1
    #print readahead.get_ref_name(alignedread.tid), alignedread.pos, alignedread.alen, alignedread.is_reverse, alignedread.is_paired, alignedread.is_proper_pair
print "chromosome", current_chromosome, "had", count, "reads"
 

readahead.close()
