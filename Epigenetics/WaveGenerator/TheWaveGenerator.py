'''
Main module for Chip-seq WaveGenerator software.  Generates the waves, which 
can be analyzed with other modules, or imported into a database for further use.
@author: afejes

'''

from WaveGenerator.Utilities import MapDecomposingThread, Parameters, WaveFileThread, \
    PrintThread, ReadAheadIteratorPET, LinkedList, MapMaker, WigFileThread, \
    MappingItem
import math
import multiprocessing
import os
import sys
import inspect
import time
import traceback
import Queue
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)
sys.path.insert(0, "..")
from WaveGenerator.Utilities import MapDecomposingThread, Parameters, WaveFileThread, \
    PrintThread, ReadAheadIteratorPET, LinkedList, MapMaker, WigFileThread, \
    MappingItem


PARAM = None

def min_index(map_queues):
    '''identify empty queues, or find the smallest queue, and put stuff there.'''
    smallest = map_queues[0].qsize()
    index = 0
    for i in range(1, len(map_queues)):
        if map_queues[i].empty():    # shortcut - just feed it an empty queue
            return i
        if map_queues[i].qsize() < smallest:
            index = i
    if smallest > 1000:
        time.sleep(1)    # slow this thread down, if it gets too far ahead.
    return index


def put_assigned(map_queues, item, max_threads):
    '''Use the min_index to determine which queue should be used.  Then place 
    the new item in the queue'''
    i = min_index(map_queues)
    try:
        map_queues[i].put(item, False)
    except Queue.Full:    # if the queue is blocking, just pick another queue
        put_assigned(map_queues, item, max_threads)
    # print ''.join([(str(queue.qsize()) + " ") for queue in map_queues])

def create_param_obj(param_file):
    PARAM = None
    if os.path.exists(param_file):
        PARAM = Parameters.parameter(param_file)
    else:
        print "Could not find input parameter file"
        sys.exit()
    return PARAM


def main(PARAM):
    '''This is the main command for running the Wave Generator peak finder.'''
    procs = []

    try:
        wave_queue = multiprocessing.Queue()
        map_queues = []
        wigfile = None    # must assign variables in case of unexpected termination.
        wavefile = None    # otherwise, they are closed, but never initialized
        print_thread = None

        global PARAM
        if os.path.exists(param_file):
            PARAM = Parameters.parameter(param_file)
            print PARAM.get_parameter("input_file")
        else:
            print "Could not find input parameter file"
            sys.exit()


        '''launch thread to read and process the print queue'''
        print_thread = PrintThread.StringWriter(print_queue)
        print_thread.start_print_writer()
        print_queue.put("Print queue and thread have started")

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

        worker_processes = PARAM.get_parameter("processor_threads")
        print ("worker processes: " + str(worker_processes))
        for x in range(worker_processes):
            queue = multiprocessing.Queue()
            map_queues.append(queue)
            mapprocessor = MapDecomposingThread.MapDecomposer(PARAM,
                                        wave_queue, print_queue, queue, x)

            p = multiprocessing.Process(target = mapprocessor.run, args = (x,))
            p.daemon = True
            try:
                p.start()
            except KeyboardInterrupt:
                p.terminate()
                for queue in map_queues:
                    queue.empty()
            procs.append(p)
        print_queue.put("All Processor threads started successfully.")
        print_queue.put("Parameters provided:")
        for par in PARAM.parameters.keys():
            print_queue.put("%s\t%s" % par, PARAM.get_parameter(par))
        print_queue.put("-------------------------------------------")

        print_queue.put("All Processor threads started successfully.")
        print_queue.put("Chromosome processing has started, along with " +
                    "threads to handle output.  Please wait until all threads " +
                    "have completed. Note, threads for processing may continue " +
                    "after the final chromosome input has been read and counted.")

        ''' Once a file is opened you can iterate over all of the read mapping to a 
        specified region using fetch(). Each iteration returns a AlignedRead object 
        which represents a single read along with its fields and optional tags:
        '''
        readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(
                    PARAM.get_parameter("input_file"),
                    PARAM.get_parameter("fragment_length"), "rb", False)
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
                if not new_block:    # flush current reads to map
                    coverage_map = mapmaker.makeIslands(block_left, block_right,
                                                        reads_list)
                    # print "adding map: ", current_chromosome, block_left
                    put_assigned(map_queues,
                                 MappingItem.Item(coverage_map, chromosome,
                                                  block_left),
                                 worker_processes)
                    if PARAM.get_parameter("make_wig"):
                        wigfile.add_map(coverage_map, current_chromosome,
                                        block_left)
                '''reset all variables to move onto new chromosome'''
                if current_chromosome != None:
                    print_queue.put("chromosome %s had %i reads" % (current_chromosome, count))
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

                    put_assigned(map_queues, MappingItem.Item(coverage_map, chromosome, block_left), worker_processes)
                    # mapprocessor.add_map(coverage_map, current_chromosome, block_left)
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

    except KeyboardInterrupt:
        print "Keyboard Interruption. ", sys.exc_info()[0]
        print traceback.format_exc()
        for queue in map_queues:
            queue.empty()    # the processes will continue to run until the queue is empty, so empty the queue to cut it short.
    except:
        print "Unexpected error in Wave Generator:", sys.exc_info()[0]
        print traceback.format_exc()
    finally:    # used to cleanly shut down the code
        print_queue.put("closing process started...")
        # Add Sentinels to end of queue
        print_queue.put("adding terminator sentinels to queue.")
        # for x in range(PARAM.get_parameter("processor_threads")):
        for queue in map_queues:
            queue.put(None)
        for proc in procs:
            proc.join()
        for queue in map_queues:
            queue.close()
        print_queue.put("Processor threads terminated. Please be patient while buffers are flushed.")
        if PARAM.get_parameter("make_wig") and wigfile != None:
            print_queue.put("Closing Wigwriter.  This may take some time.")
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
        print "Shutdown complete"

counter = 0

if __name__ == "__main__":
    if len(sys.argv) > 0 :
        for arg in sys.argv:
            print arg
    # sys.argv[1] must be equal to the file name of the input file.
    print_queue = multiprocessing.Queue()
    PARAM = create_param_obj(sys.argv[1])
    main(PARAM)

