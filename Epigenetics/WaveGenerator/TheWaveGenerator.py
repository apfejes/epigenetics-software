'''
Main module for Chip-seq WaveGenerator software.  Generates the waves, which 
can be analyzed with other modules, or imported into a database for further use.
@author: afejes

'''

from Utilities import MapDecomposingThread, Parameters, WaveFileThread, \
    PrintThread, ReadAheadIteratorPET, LinkedList, MapMaker, WigFileThread
import math
import multiprocessing
import os
import sys
import time
import traceback
import cProfile


PARAM = None

def main(param_file):
    '''This is the main command for running the Wave Generator peak finder.'''
    procs = []

    try:

        wave_queue = multiprocessing.Queue()
        map_queue = multiprocessing.Queue(200)
        wigfile = None    # must asign variables in case of unexpected termination.
        wavefile = None    # otherwise, they are closed, but never initialized
        print_thread = None

        global PARAM
        if os.path.exists(param_file):
            PARAM = Parameters.parameter(param_file)
            print PARAM.get_parameter("input_file")
        else:
            print "Could not find input parameter file"
            sys.exit()



        ''' Once a file is opened you can iterate over all of the read mapping to a 
        specified region using fetch(). Each iteration returns a AlignedRead object 
        which represents a single read along with its fields and optional tags:
        '''
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(
                    PARAM.get_parameter("input_file"),
                    PARAM.get_parameter("fragment_length"), "rb", False)
        current_chromosome = None
        count = 0
        new_block = True
        block_left = 0
        block_right = 0
        reads_list = LinkedList.LL()
        mapmaker = MapMaker.MapMaker(PARAM)
        if PARAM.get_parameter("make_wig"):    # processor threads
            wigfile = WigFileThread.WigFileWriter(None)
            wigfile.start_wig_writer(PARAM.get_parameter('output_path'),
                                     PARAM.get_parameter('file_name'))
        wavefile = WaveFileThread.WaveFileWriter(None, wave_queue)
        wavefile.start_wave_writer(PARAM.get_parameter('output_path'),
                                   PARAM.get_parameter('file_name'))

        '''launch thread to read and process the print queue'''
        print_thread = PrintThread.StringWriter(print_queue)
        print_thread.start_print_writer()


        for x in range(PARAM.get_parameter("processor_threads")):
            p = None
            mapprocessor = MapDecomposingThread.MapDecomposer(PARAM,
                                        wave_queue, print_queue, map_queue, x)
            print x
            if x == 0:
                p = multiprocessing.Process(target = cProfile.runctx("mapprocessor.run", globals(), locals()))
                # p = cProfile.runctx(multiprocessing.Process(target = mapprocessor.run, args = (x,)), globals(), locals(), "file_%d" % x)
            else:
                p = multiprocessing.Process(target = mapprocessor.run)
            p.daemon = True
            p.start()
            procs.append(p)

        print_queue.put("All Processor threads started successfully.")
        print_queue.put("Chromosome processing has started, along with " +
                    "threads to handle output.  Please wait until all threads " +
                    "have completed. Note, threads for processing may continue " +
                    "after the final chromosome input has been read and counted.")
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
                if alignedreadobjpet.is_pet() and math.fabs(read_left - read_right) > PARAM.get_parameter("max_pet_length"):
                    continue    # simply move to the
                if not new_block:
                # flush current reads to map
                    coverage_map = mapmaker.makeIslands(block_left, block_right,
                                                        reads_list)
                    # print "adding map: ", current_chromosome, block_left
                    mapprocessor.add_map(coverage_map, current_chromosome,
                                         block_left)
                    if PARAM.get_parameter("make_wig"):
                        wigfile.add_map(coverage_map, current_chromosome,
                                        block_left)
                '''reset all variables to move onto new chromosome'''
                if current_chromosome != None:
                    print "chromosome", current_chromosome, "had", count, "reads"
                current_chromosome = chromosome
                reads_list.destroy()
                new_block = True
                count = 0
                ''' end new chromosome '''
            count += 1

            read_left = alignedreadobjpet.get_left_end()
            read_right = alignedreadobjpet.get_right_end()
            if alignedreadobjpet.is_pet() and math.fabs(read_left - read_right) > PARAM.get_parameter("max_pet_length"):
                continue
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
                    mapprocessor.add_map(coverage_map, current_chromosome,
                                         block_left)
                    if PARAM.get_parameter("make_wig"):
                        wigfile.add_map(coverage_map, current_chromosome,
                                        block_left)
                    reads_list.destroy()
                    new_block = True
                    ''' push back the current read, so we can start again with a 
                    new block'''
                    readahead.pushback(alignedreadobjpet)

        print_queue.put("chromosome " + current_chromosome + " had " +
                        str(count) + " reads")
        print_queue.put("Completed all Processing - Shutting down.")
    except:
        print "Unexpected error in Wave Generator:", sys.exc_info()[0]
        print traceback.format_exc()


    finally:
        print_queue.put("closing process started...")
        while map_queue.qsize() > 0:
            print_queue.put("waiting on map_queue to empty")
            time.sleep(3)
        MapDecomposingThread.END_PROCESSES = True
        map_queue.close()
        for proc in procs:
            proc.terminate()
        # MapDecomposingThread.queue.join_thread()
        print_queue.put("Processor threads terminated.")
        if PARAM.get_parameter("make_wig") and wigfile != None:
            wigfile.close_wig_writer()
            print_queue.put("Wigwriter closed.")

        while wave_queue.qsize() > 0:
            print_queue.put("waiting on wave_queue to empty")
            time.sleep(1)
        if wavefile != None:
            wavefile.close_wave_writer()
        wave_queue.close()
        print_queue.put("wave_queue closed")

        if print_thread == None or not print_thread.is_alive():
            pass
        else:
            while print_queue.qsize() > 0:
                print "waiting on print_queue to empty", print_queue.qsize()
                time.sleep(1)
            print_thread.END_PROCESSES = True
        # print_queue.close()
        print  ("print_queue closed")
        # print_queue.join()

        readahead.close()
        print "all closed"

if __name__ == "__main__":
    if len(sys.argv) > 0 :
        for arg in sys.argv:
            print arg
    # sys.argv[1] must be equal to the file name of the input file.

    print_queue = multiprocessing.Queue()
    main(sys.argv[1])
