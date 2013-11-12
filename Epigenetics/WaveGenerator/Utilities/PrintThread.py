'''
Created on 2013-03-08

@author: afejes
'''


import threading
import sys
import traceback
import Queue
import exceptions
import os



queue = None

class StringWriter(threading.Thread):
    '''This class handles a multithreaded queue, allowing all threads to dump 
    their output text or other messages into a single location.  This prevents 
    concurrency issues and allows a multithreaded/multiprocess program to have 
    consistently clean output.'''



    def __init__(self, queue_var, output_path = None, file_name = None, supress_print = False, thread = True):
        '''initialize the StringWriter'''

        threading.Thread.__init__(self)
        global queue    # IGNORE:W0603 - acceptable use of a global variable.
        queue = queue_var

        self.supress_print = supress_print
        self.IS_CLOSED = True
        self.END_PROCESSES = False
        if file_name != None:
            self.printout = True
            path = os.path.dirname(os.path.abspath(__file__))
            path = path.rsplit("/", 1)
            self.f = open(output_path + '/' + file_name, 'w')
            self.IS_CLOSED = False
        else:
            self.printout = False
        if thread:
            self.setDaemon(True)
            self.start()


    @staticmethod
    def type():
        '''announces that this object is a String writer of the PrintThread, if asked'''
        return "PrintThread.StringWriter"

    def process_string(self, string):
        '''process strings being sent to the print thread'''
        if (self.printout):
            self.f.write(string)
            self.f.write("\n")
        if (not self.supress_print):
            print string

    def run(self):
        '''run the process - handle incoming threads'''
        # global queue
        while not self.END_PROCESSES:
            try:
                if queue is None:
                    break
                string = queue.get()    # grabs string from queue
                self.process_string(string)    # print retrieved string
            except Queue.Empty():
                if self.END_PROCESSES:
                    self.f.close()
                    break
                else:
                    continue
            except exceptions.IOError:
                pass    # ignoring this error - it's normal, and a known error.
                # http://bugs.python.org/issue5155
            except exceptions.EOFError:
                pass
            except:
                print "Unexpected error in print thread:", sys.exc_info()[0]
                print traceback.format_exc()
            # except self.queue.Empty:
            #    if END_PROCESSES:
            #        self.print_queue.put("thread received signal to quit")
            #        break
            #    else:
            #        continue'''
        try:
            if queue != None:
                while queue.qsize() > 0:
                    string = queue.get()    # grabs string from queue
                    self.process_string(string)    # print retrieved string
        finally:
            self.f.close()
            self.IS_CLOSED = True

    def is_closed(self):
        return self.IS_CLOSED

