'''
Created on 2013-03-08

@author: afejes
'''


import threading
import sys
import traceback
import Queue
import exceptions
from exceptions import EOFError, IOError
END_PROCESSES = False


class StringWriter(threading.Thread):
    '''This class handles a multithreaded queue, allowing all threads to dump 
    their output text or other messages into a single location.  This prevents 
    concurrency issues and allows a multithreaded/multiprocess program to have 
    consistently clean output.'''


    def __init__(self, queue_var):
        threading.Thread.__init__(self)
        global queue
        queue = queue_var

    @staticmethod
    def type():
        return "PrintThread.StringWriter"

    @staticmethod
    def process_string(string):
        print string

    def run(self):
        # global queue
        while not END_PROCESSES:
            try:
                if queue == None:
                    break
                string = queue.get()    # grabs string from queue
                self.process_string(string)    # print retrieved string
            except Queue.Empty():
                if END_PROCESSES:
                    print("print thread received signal to quit")
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


    def start_print_writer(self):
        # spawn a pool of threads, and pass them queue instance
        global queue
        self.t = StringWriter(queue)
        self.t.setDaemon(True)
        self.t.start()


