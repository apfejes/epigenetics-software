'''
Main module for Chip-seq WaveGenerator software.  Generates the waves, which 
can be analyzed with other modules, or imported into a database for further use.
@author: afejes, sbrown

'''


import time
import math
import multiprocessing
import traceback
import Queue
import os
import sys

from random import randint
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")    # add the utilities folder here

# Modules in Utilities
import MapDecomposingThread
import Parameters
import WaveFileThread
import PrintThread
import ReadAheadIteratorPET
import LinkedList
import MapMaker
import WigFileThread
import MappingItem

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")

import StringUtils



def random_index(num_queues):
    '''TODO:missing doc string'''
    return randint(0, num_queues - 1)


def min_index(map_queues, max_threads):
    '''identify empty queues, or find the smallest queue, and put stuff there.'''
    smallest = map_queues[0].qsize()
    index = 0
    for i in range(1, max_threads):
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
    i = random_index(max_threads)
    # i = min_index(map_queues, max_threads)
    try:
        map_queues[i].put(item, False)
    except Queue.Full:    # if the queue is blocking, just pick another queue
        put_assigned(map_queues, item, max_threads)
    # print ''.join([(str(queue.qsize()) + " ") for queue in map_queues])

def create_param_obj(param_file):
    '''TODO:missing doc string'''
    p = None
    if os.path.exists(param_file):
        p = Parameters.parameter(param_file)
    else:
        print "Could not find input parameter file"
        sys.exit()
    return p

def process_BAM_reads(PARAM, mapmaker, map_queues, print_queue, wigfile, worker_processes):
    '''TODO:missing doc string'''
    current_chromosome = None
    count = 0
    new_block = True
    block_left = 0
    block_right = 0
    reads_list = LinkedList.LL()
    readahead = ReadAheadIteratorPET.ReadAheadIteratorPET(
                    PARAM.get_parameter("input_file"),
                    PARAM.get_parameter("fragment_length"), "rb", False)
    while True:
        # print count, "reads processed"
        alignedreadobjpet = readahead.getNext()
        if not readahead.isReadValid:
            break
        if (alignedreadobjpet is None) :
            # flush chromosomome related objects, then continue
            continue
        chromosome = readahead.get_ref_name(alignedreadobjpet.read1.tid)
        if current_chromosome != chromosome:
            # push currently buffered reads to map maker, so mapping can begin
            # again from the start of the next chromosome.
            read_left = alignedreadobjpet.left_end()
            read_right = alignedreadobjpet.right_end()
            if alignedreadobjpet.is_pet() and math.fabs(read_left - read_right) > PARAM.get_parameter("max_pet_length"):
                continue    # simply move to the
            if not new_block:    # flush current reads to map
                coverage_map = mapmaker.makeIslands(block_left, block_right,
                                                    reads_list)
                # print "adding map: ", current_chromosome, block_left
                put_assigned(map_queues,
                             MappingItem.Item(coverage_map, current_chromosome,
                                              block_left),
                             worker_processes)
                if PARAM.get_parameter("make_wig"):
                    wigfile.add_map(coverage_map, current_chromosome,
                                    block_left)
            # reset all variables to move onto new chromosome
            if current_chromosome != None:
                print_queue.put("chromosome %s had %i reads" % (current_chromosome, count))
            current_chromosome = chromosome
            reads_list.destroy()
            new_block = True
            count = 0
            # end new chromosome
        count += 1

        read_left = alignedreadobjpet.left_end
        read_right = alignedreadobjpet.right_end
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
                # push back the current read, so we can start again with a new block
                readahead.pushback(alignedreadobjpet)
    print_queue.put("chromosome " + current_chromosome + " had " +
                        str(count) + " reads")
    readahead.close()

def process_WIG_reads(PARAM, map_queues, print_queue, worker_processes):
    '''TODO:missing doc string'''
    current_chromosome = None
    count = 0
    position = 0
    filereader = open(PARAM.get_parameter("input_file"), 'r')
    thismap = []
    chromosome = ""
    firstpass = True
    for line in filereader:
        if line.startswith('track'):
            continue
        if line.startswith('fixedStep'):
            count += 1
            if not firstpass:
                ##this dumps the previous region into queue
                put_assigned(map_queues,
                             MappingItem.Item(thismap, current_chromosome,
                                              position),
                             worker_processes)  
            else:
                firstpass = False
            #now look at current region
            a = line.split()
            t = a[1].split("=")
            chromosome = t[1]
            t = a[2].split("=")
            position = int(t[1])
            # print "chromosome and position (%s, %i)" % (chromosome, position)
            # process array that you've built - send it to the map processor
            thismap = []
            # break string into components
            # get chromosome name and position of map
            

            if chromosome != current_chromosome:
                if current_chromosome != None:
                    print_queue.put("chromosome %s had %i regions of enrichment" % (current_chromosome, count-1))
                    #count-1 since remove first 'fixedStep' of new chrom.
                    count = 1 #to take into account the first 'fixedStep' line of new chrom.
                current_chromosome = chromosome
                #count = 0
        else:
            thismap.append(float(line))
    #endfor
    if len(thismap) > 0:
        put_assigned(map_queues, MappingItem.Item(thismap, current_chromosome, position), worker_processes)
    print_queue.put("chromosome %s had %i regions of enrichment" % (current_chromosome, count))
    filereader.close()




def main(PARAM):
    '''This is the main command for running the Wave Generator peak finder.'''
    procs = []


    try:
        wave_queue = multiprocessing.Queue()
        print_queue = multiprocessing.Queue()
        map_queues = []
        wigfile = None    # must assign variables in case of unexpected termination.
        wavefile = None    # otherwise, they are closed, but never initialized
        print_thread = None

        # launch thread to read and process the print queue'''
        # print_thread = PrintThread.StringWriter(print_queue)
        #print_thread = PrintThread.StringWriter(print_queue, "/home/afejes/temp/", "wavegenerator.txt", False, True)
        print_thread = PrintThread.StringWriter(print_queue, PARAM.get_parameter("output_path"), PARAM.get_parameter("file_name")+"_wavegenerator.txt", False, True)
        print_queue.put("Print queue and thread have started")


        if PARAM.get_parameter("input_file").endswith('wig'):
            PARAM.set_parameter('type', "WIG")
            if PARAM.get_parameter("make_wig"):
                PARAM.set_parameter("make_wig", False)
                print_queue.put("Disabling Wig file generation for wig file input.")
        elif (PARAM.get_parameter("input_file").endswith('bam') or
              PARAM.get_parameter("input_file").endswith('sam')):
            PARAM.set_parameter('type', "BAM")
        else:
            print_queue.put("Unrecognized file format extension for file: "
                         % (PARAM.get_parameter("input_file")))

        # TODO: test if file exists.



        if PARAM.get_parameter("make_wig"):    # processor threads
            wigfile = WigFileThread.WigFileWriter(None)
            wigfile.start_wig_writer(PARAM.get_parameter('output_path'),
                                     PARAM.get_parameter('file_name'))
        wavefile = WaveFileThread.WaveFileWriter(None, wave_queue)
        wavefile.start_wave_writer(PARAM.get_parameter('output_path'),
                                   PARAM.get_parameter('file_name'))

        worker_processes = PARAM.get_parameter("processor_threads")
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
            print_queue.put("%s\t%s" % (par, PARAM.get_parameter(par)))
        print_queue.put("-------------------------------------------")

        print_queue.put("Chromosome processing has started, along with " +
                    "threads to handle output.  Please wait until all threads " +
                    "have completed. Note, threads for processing may continue " +
                    "after the final chromosome input has been read and counted.")

        # Once a file is opened you can iterate over all of the read mapping to a
        # specified region using fetch(). Each iteration returns a AlignedRead object
        # which represents a single read along with its fields and optional tags:
        if PARAM.get_parameter('type') == "WIG":
            process_WIG_reads(PARAM, map_queues, print_queue, worker_processes)
        elif PARAM.get_parameter('type') == "BAM":
            mapmaker = MapMaker.MapMaker(PARAM)
            print_queue.put("Initialized MapMaker object, to convert reads to maps. (completed)")
            process_BAM_reads(PARAM, mapmaker, map_queues, print_queue, wigfile, worker_processes)
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
        temp = -1
        print_queue.put("terminator sentinels have been added - will poll queue sizes until processing is complete ")
        while temp != 0:
            temp = 0
            for x in range(len(map_queues)):
                temp += map_queues[x].qsize()

            pause = temp / 1000
            if pause > 20:
                pause = 20
            if pause < 2:
                pause = 2
            print_queue.put("there are %i items remaining in the map queue.  will poll again in %i seconds" % (temp, pause))
            time.sleep(pause)
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

        if print_thread is None or not print_thread.is_alive():
            pass
        else:
            while print_queue.qsize() > 0:
                print "waiting on print_queue to empty", print_queue.qsize()
                time.sleep(1)
            print_thread.END_PROCESSES = True
        print  ("print_queue closed")

        print "Shutdown complete"

if __name__ == "__main__":
    '''
    if len(sys.argv) > 0 :
        for arg in sys.argv:
            print arg
    # sys.argv[1] must provide the file name of the input file.
    '''
       
    if len(sys.argv) <= 1 :
        print "USAGE: python TheWaveGenerator.py param.file [input_file [output_path]]"
        
        sys.exit()

    param = create_param_obj(sys.argv[1])
    
    #override parameter file with cmdline args
    if len(sys.argv) >= 3 :
        param.set_parameter("input_file", sys.argv[2]) #override input_file
        #set file_name in param to be based on input file.
        ofile = StringUtils.rreplace(os.path.basename(sys.argv[2]), '.wig', '', 1)
        param.set_parameter("file_name", ofile) #override output file_name (.waves gets added later)
    if len(sys.argv) == 4 :
        param.set_parameter("output_path", sys.argv[3]) #override output_path
        
    print "param file: ",sys.argv[1]
    print "input_file: ",param.get_parameter("input_file")
    print "output_path: ",param.get_parameter("output_path")
    print "output_file_name: ",param.get_parameter("file_name")
    
        
    main(param)

