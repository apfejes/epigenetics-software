'''
Created on 2013-03-08

@author: afejes
'''

import threading
import os

class wave():

    def __init__(self, chromosome, crest, sigma, height, number):
        self.chromosome = chromosome
        self.crest = crest
        self.sigma = sigma
        self.height = height
        self.number = number

    def type(self):
        return "Wave"


class WaveFileWriter(threading.Thread):

    # f = None
    # t = None

    def type(self):
        return "WaveFileThread"

    def __init__(self, filewriter, wave_queue):
        threading.Thread.__init__(self)
        self.queue = wave_queue
        self.f = filewriter

    def process_wave(self, wave):
        if (wave.number != None):
            self.f.write(wave.chromosome + "\t" + str(wave.crest) + "\t" + str(wave.sigma) + "\t" + str(wave.height) +
                         "\t" + str(wave.number) + "\n")
        else:
            self.f.write(wave.chromosome + "\t" + str(wave.crest) + "\t" + str(wave.sigma) + "\t" + str(wave.height) + "\n")

    def run(self):
        while True:
            # grabs host from queue
            wave = self.queue.get()
            self.process_wave(wave)
            # signals to queue job is done
            # self.queue.task_done()


    def start_wave_writer(self):
        # spawn a pool of threads, and pass them queue instance
#        for i in range(1):
        path = os.path.dirname(os.path.abspath(__file__))
        path = path.rsplit("/", 1)
        self.f = open(path[0] + '/testdata/tmp/findwaves.waves', 'w', 0)    # currently unbuffered - remove zero to buffer
        self.f.write("# This wave file was generated by WaveGenerator 0.1, written by Anthony P. Fejes\n")
        self.f.write("# Wavewriter Version: 0.1\n")
        self.f.write("# Chromosome\tcrest pos.\tstd_dev\theight\tnumber\n")

        for _i in range(1):
            self.t = WaveFileWriter(self.f, self.queue)
            self.t.setDaemon(True)
            self.t.start()


    def close_wave_writer(self):
        self.f.close()



        # wait on the queue until everything has been processed

