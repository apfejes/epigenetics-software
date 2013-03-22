'''
Created on 2013-03-08

@author: afejes
'''


import threading
import sys
END_PROCESSES = False


class StringWriter(threading.Thread):
    '''This class handles a multithreaded queue, allowing all threads to dump 
    their output text or other messages into a single location.  This prevents 
    concurrency issues and allows a multithreaded/multiprocess program to have 
    consistently clean output.'''


    def __init__(self, queue_var):
        threading.Thread.__init__(self)

        self.queue = queue_var

    @staticmethod
    def type():
        return "PrintThread.StringWriter"

    @staticmethod
    def process_string(string):
        print string

    def run(self):
        while True:
            try:
                if self.queue == None:
                    break
                string = self.queue.get()    # grabs string from queue
                self.process_string(string)    # print retrieved string
            except:
                print "Unexpected error:", sys.exc_info()[0]
                sys.exit()
            # except self.queue.Empty:
            #    if END_PROCESSES:
            #        self.print_queue.put("thread received signal to quit")
            #        break
            #    else:
            #        continue'''


    def start_print_writer(self):
        # spawn a pool of threads, and pass them queue instance
        self.t = StringWriter(self.queue)
        self.t.setDaemon(True)
        self.t.start()


