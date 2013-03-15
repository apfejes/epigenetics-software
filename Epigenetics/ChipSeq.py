
from Utilities import ReadAheadIteratorPET, LinkedList, MapMaker, WigFileThread
from Utilities import MapDecomposingThread, Parameters, WaveFileThread



param = Parameters.parameter()
param.set_parameter("make_wig", True)
param.set_parameter("fragment_length", 350)
param.set_parameter("map_type", "Triangle")
param.set_parameter("min_height", 10)


''' Once a file is opened you can iterate over all of the read mapping to a 
specified region using fetch(). Each iteration returns a AlignedRead object 
which represents a single read along with its fields and optional tags:
'''

readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(
            "testdata/ChipSeqGSE31221/GSE31221_RAW/" +
            "18_19_GSM773994_TCF7_ChIPSeq.bam",
            param.get_parameter("fragment_length"), "rb", False)
current_chromosome = None
count = 0;
new_block = True;
last_block_l = 0
last_block_r = 0
block_left = 0
block_right = 0
reads_list = LinkedList.LL()
mapmaker = MapMaker.MapMaker(param.get_parameter("map_type"), 100,
                             200, param.get_parameter("fragment_length")
                             )
'''processor threads'''
if param.get_parameter("make_wig"):
    wigfile = WigFileThread.WigFileWriter(None)
    wigfile.start_wig_writer()
wavefile = WaveFileThread.WaveFileWriter(None)
wavefile.start_wave_writer()
mapprocessor = MapDecomposingThread.MapDecomposer(param, wavefile)
mapprocessor.start_map_decomposer()

print "Threads Started."
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
        '''push currently buffered reads to map maker, so mapping can begin 
        again from the start of the next chromosome.'''
        read_left = alignedreadobjpet.get_left_end()
        read_right = alignedreadobjpet.get_right_end()
        if not new_block:
        # flush current reads to map
            coverage_map = mapmaker.makeIslands(block_left, block_right,
                                                reads_list)
            # print "adding map: ", current_chromosome, block_left
            mapprocessor.add_map(coverage_map, current_chromosome, block_left)
            if param.get_parameter("make_wig"):
                wigfile.add_map(coverage_map, current_chromosome, block_left)
        '''reset all variables to move onto new chromosome'''
        if current_chromosome != None:
            print "chromosome", current_chromosome, "had", count, "reads"
        current_chromosome = chromosome
        reads_list.destroy()
        new_block = True
        last_block_l = 0
        last_block_r = 0
        count = 0
        ''' end new chromosome '''
    count += 1

    read_left = alignedreadobjpet.get_left_end()
    read_right = alignedreadobjpet.get_right_end()

    if new_block:
        reads_list = LinkedList.LL()
        block_left = read_left
        block_right = read_right
        new_block = False
        reads_list.append(alignedreadobjpet)
    else:
        if block_right >= read_left:
            reads_list.append(alignedreadobjpet)
            if block_right < read_right:
                block_right = read_right
        else:
            coverage_map = mapmaker.makeIslands(block_left, block_right,
                                                reads_list)
            mapprocessor.add_map(coverage_map, current_chromosome, block_left)
            if param.get_parameter("make_wig"):
                wigfile.add_map(coverage_map, current_chromosome, block_left)
            reads_list.destroy()
            new_block = True
            last_block_l = block_left
            last_block_r = block_right
            readahead.pushback(alignedreadobjpet)    # push back the current
                                # read, so we can start again with a new block
print "chromosome", current_chromosome, "had", count, "reads"

mapprocessor.close_map_decomposer()
if param.get_parameter("make_wig"):
    wigfile.close_wig_writer()
wavefile.close_wave_writer()
readahead.close()
