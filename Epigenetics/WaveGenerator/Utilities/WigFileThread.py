'''
Created on 2013-03-08

@author: afejes
'''

import Queue
import threading
import MappingItem
import os

queue = Queue.Queue()



class WigFileWriter(threading.Thread):
    '''Filewriter that outputs in the form of a wig file'''

    def __init__(self, filewriter):
        '''initialize the filewriter'''
        threading.Thread.__init__(self)
        self.queue = queue
        self.t = None    # thread
        if filewriter != None:
            self.f = filewriter

    def process_map(self, item):
        '''convert a single map (array/list of integers) to a single "fixedstep" region'''
        if item.start >= 0:    # drop entire maps that start before the 0th position.
            # TODO: a more elegant solution would be to trim the positions until they start at zero.
            self.f.write("\nfixedStep chrom=%s start=%i step=1\n" % (item.chr, item.start))
            self.f.write('\n'.join([str(s) for s in item.coverage_map]))


    def run(self):
        ''' start the file writer - accept objects from the queue and processes 
        them, writing out when done.'''
        while True:
            # grabs host from queue
            map_item = self.queue.get()
            self.process_map(map_item)
            # signals to queue job is done
            self.queue.task_done()


    def start_wig_writer(self, output_path, file_name, trackname = 'WaveGenerator', ucsc = False):
        '''generate the required header for the output wig file.'''
        path = os.path.dirname(os.path.abspath(__file__))
        path = path.rsplit("/", 1)
        self.f = open(output_path + '/' + file_name + '.wig', 'w')
        if ucsc:
            self.f = open(path[0] + '/testdata/tmp/findwaves.wig', 'w')
            self.f.write("# This wig file was generated by WaveGenerator 0.1, written by Anthony P. Fejes\n")
            self.f.write("# Wigwriter Version: 0.1\n")
        self.f.write("track type=wiggle_0 name='" + trackname + "' description='Testing Wave Generator' ")
        if ucsc:
            self.f.write("color=50,50,150 ")
            self.f.write("yLineMark=0.0 ")
            self.f.write("yLineOnOff=on ")
            self.f.write("visibility=2 ")
            self.f.write("priority=1 ")
            self.f.write("autoScale=on ")
            self.f.write("maxHeightPixels=40:40:2\n")
        self.t = WigFileWriter(self.f)
        self.t.setDaemon(True)
        self.t.start()


    def close_wig_writer(self):
        '''close the filewriter'''
        queue.join()

        if (self.f != None):
            self.f.close()

    @staticmethod
    def add_map(map_region, chromosome, start):
        '''add a map to the queue for processing'''
        # populate queue with data
        queue.put(MappingItem.Item(map_region, chromosome, start))
        # wait on the queue until everything has been processed
