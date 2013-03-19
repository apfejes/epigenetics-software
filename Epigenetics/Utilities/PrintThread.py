'''
Created on 2013-03-08

@author: afejes
'''


import threading


class StringWriter(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    @staticmethod
    def type():
        return "PrintThread.StringWriter"

    def process_string(self, string):
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

    def close_wig_writer(self):
        self.queue.join()
        self.queue.all_tasks_done

