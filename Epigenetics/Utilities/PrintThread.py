'''
Created on 2013-03-08

@author: afejes
'''


import threading


class StringWriter(threading.Thread):
    '''This class handles a multithreaded queue, allowing all threads to dump 
    their output text or other messages into a single location.  This prevents 
    concurrency issues and allows a multithreaded/multiprocess program to have 
    consistently clean output.'''


    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    @staticmethod
    def type():
        return "PrintThread.StringWriter"

    @staticmethod
    def process_string(string):
        print string

    def run(self):
        while True:
            # grabs host from queue
            string = self.queue.get()
            # print "got", string
            self.process_string(string)
            # signals to queue job is done
            # self.queue.task_done()

    def start_print_writer(self):
        # spawn a pool of threads, and pass them queue instance
        self.t = StringWriter(self.queue)
        self.t.setDaemon(True)
        self.t.start()

    def close_print_writer(self):
        pass

