
from Utilities import ReadAheadIteratorPET, LinkedList, MapMaker, WigFileThread
from Utilities import MapDecompingThread, Parameters


param = Parameters.parameter()
param.set_parameter("make_wig", True)
param.set_parameter("fragment_length", 250)
param.set_parameter("map_type", "Triangle")
param.set_parameter("min_height", 4)




# Once a file is opened you can iterate over all of the read mapping to a specified region using fetch(). Each iteration returns a AlignedRead object which represents a single read along with its fields and optional tags:


# do something with input

readahead = ReadAheadIteratorPET.ReadAheadIteratorPET("testdata/ChipSeqGSE31221/GSE31221_RAW/18_19_GSM773994_TCF7_ChIPSeq.bam",
                                                       param.get_parameter("fragment_length"), "rb", False)
current_chromosome = None
count = 0;
new_block = True;
last_block_l = 0
last_block_r = 0
reads_list = LinkedList.LL()
mapmaker = MapMaker.MapMaker(param.get_parameter("map_type"), 50, 150, param.get_parameter("fragment_length")
                             )
'''processor threads'''
if param.get_parameter("make_wig"):
    wigfile = WigFileThread.WigFileWriter(None)
    wigfile.start_wig_writer()
mapprocessor = MapDecompingThread.MapDecomposer(param)
mapprocessor.start_map_decomposer()






while True:
    # print count, "reads processed"
    alignedreadobjpet = readahead.getNext()
    if not readahead.isReadValid:
        break
    if (alignedreadobjpet == None) :
        # flush chromosomome related objects, then continue
        continue
    chromosome = readahead.get_ref_name(alignedreadobjpet.read1.tid)
    if current_chromosome != chromosome:
        if current_chromosome != None:
            print "chromosome", current_chromosome, "had", count, "reads"
        current_chromosome = chromosome
        '''reset blocks, so mapping can begin again from the start of the chromosome.'''
        new_block = True
        last_block_l = 0
        last_block_r = 0
        count = 0

        # flush current reads to map.


    count += 1

    read_left = alignedreadobjpet.get_left_end()
    read_right = alignedreadobjpet.get_right_end()

    if new_block:
        reads_list = LinkedList.LL()
        block_left = read_left
        block_right = read_right
        new_block = False
        reads_list.append(alignedreadobjpet)
        # print "new block:", block_left, "-", block_right
    else:
        if block_right >= read_left:
            # print "block added.", block_left, "-", block_right, "read", read_left , "-", read_right
            reads_list.append(alignedreadobjpet)
            if block_right < read_right:
                block_right = read_right
                # print "block extended:", block_left, "-", block_right
        else:
            coverage_map = mapmaker.makeIslands(block_left, block_right, reads_list)
            # print "adding map: ", current_chromosome, block_left
            mapprocessor.add_map(coverage_map, current_chromosome, block_left)
            if param.get_parameter("make_wig"):
                wigfile.add_map(coverage_map, current_chromosome, block_left)
            reads_list.destroy()
            new_block = True
            last_block_l = block_left
            last_block_r = block_right
            readahead.pushback(alignedreadobjpet)    # push back the current read, so we can start again with a new block




    # print readahead.get_ref_name(alignedread.tid), alignedread.pos, alignedread.alen, alignedread.is_reverse, alignedread.is_paired, alignedread.is_proper_pair
print "chromosome", current_chromosome, "had", count, "reads"

mapprocessor.close_map_decomposer()
if param.get_parameter("make_wig"):
    wigfile.close_wig_writer()
readahead.close()
