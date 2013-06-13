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
END_PROCESSES = False

class StringWriter(threading.Thread):
    '''This class handles a multithreaded queue, allowing all threads to dump 
    their output text or other messages into a single location.  This prevents 
    concurrency issues and allows a multithreaded/multiprocess program to have 
    consistently clean output.'''



    def __init__(self, queue_var, output_path = None, file_name = None, supress_print = False, thread = False):
        threading.Thread.__init__(self)
        global queue
        queue = queue_var
        self.supress_print = supress_print
        if file_name != None:
            self.printout = True
            path = os.path.dirname(os.path.abspath(__file__))
            path = path.rsplit("/", 1)
            self.f = open(output_path + '/' + file_name, 'w')
        else:
            self.printout = False
        if thread:
            self.setDaemon(True)
            self.start()


    @staticmethod
    def type():
        return "PrintThread.StringWriter"

    def process_string(self, string):
        if (self.printout):
            self.f.write(string)
            self.f.write("\n")
        if (not self.supress_print):
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


