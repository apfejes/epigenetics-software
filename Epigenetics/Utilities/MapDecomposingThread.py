'''
Created on 2013-03-08

@author: afejes
'''

import Queue
import threading
import math
import copy
import numpy
from Utilities import WaveFileThread, MappingItem

queue = Queue.Queue()

class MapDecomposer(threading.Thread):

    f = None
    t = None
    param = None
    sigma_height_table = None

    def __init__(self, param):
        threading.Thread.__init__(self)
        self.queue = queue
        if (MapDecomposer.param == None):
            MapDecomposer.param = param
        if (MapDecomposer.sigma_height_table == None):
            MapDecomposer.sigma_height_table = numpy.ndarray((300, 900))
            '''first variable is the sigma, second is the number of spaces away from the centre of the peak'''
            for i in xrange(1, 300):    # sigma - which can't be = to zero
                for j in xrange(900):    # distance from peak
                    MapDecomposer.sigma_height_table[i][j] = MapDecomposer.gausian_value_at_x(i, 0, j)
                MapDecomposer.sigma_height_table[i][0] = MapDecomposer.gausian_value_at_peak(i)

    @staticmethod
    def get_tallest_point(coverage_map):
        '''returns position and height of the highest point in the map'''
        pos = 0
        height = 0
        for i in range(0, len(coverage_map)):
            if height < coverage_map[i] :
                height = coverage_map[i]
                pos = i
        return {'position':pos, 'height':height}


    @staticmethod
    def gausian_value_at_x(sigma, mu, x):
        '''
        sigma is the standard deviation
        mu is the mean (median/mode) of the distribution
        '''
        f = 1.0 / (float(sigma) * math.sqrt(2.0 * math.pi))
        n = float(x - mu)
        m = ((n * n) / (2.0 * float(sigma) * float(sigma)))
        return f * math.exp(-m)

    @staticmethod
    def gausian_value_at_peak(sigma):
        '''use this to figure out this the max height of the gausian. The e^whatever turns into e^0 = 1.'''
        f = 1.0 / (sigma * math.sqrt(2.0 * math.pi))
        return f

    @staticmethod
    def subtract_gausian(coverage_map, height, sigma, mu):
        max_ht = MapDecomposer.gausian_value_at_peak(sigma)
        s = sigma * 3
        for i in range(-s, s):
            if (i + mu >= 0 and i + mu < len(coverage_map)):
                # print "coverage_map[", i + mu, "]", coverage_map[i + mu], "-", (height * (MapDecomposer.sigma_height_table[sigma][math.fabs(i)] / max_ht)) =
                coverage_map[i + mu] -= (height * (MapDecomposer.sigma_height_table[sigma][math.fabs(i)] / max_ht))
        return coverage_map



    def best_fit_test(self, coverage_map, i):
        '''i is the position to test for the best fit in the coverage_map.'''
        # print "start best_fit_test"
        sigma = 1
        height = coverage_map[i]
        while True:
            area_over = 0
            area_under = 0
            s = 3 * sigma

            for x in xrange(-s, s):
                if (i + x >= 0 and x < 900 and i + x < len(coverage_map)):
                    # print x
                    expected = MapDecomposer.sigma_height_table[sigma][math.fabs(x)] * height / MapDecomposer.sigma_height_table[sigma][0]
                    # print "sigma:", sigma, "i,x:", i, x, "(", MapDecomposer.sigma_height_table[sigma][math.fabs(x)], "*", height, "/", MapDecomposer.sigma_height_table[sigma][0], "=", expected, ")"
                    actual = -1
                    if i + x >= 0:
                        actual = coverage_map[i + x]
                    else:
                        actual = -1
                    if actual < expected:
                        area_over += expected - actual
                        area_under += actual
                    elif actual > expected:
                        area_under += expected
            if (area_over > 0.01 * area_under) or sigma > 400:
                break
            sigma += 1

        # print "sigma returned:", sigma
        return sigma


    def process_map(self, item):
        peaks = []
        n = copy.deepcopy(item.coverage_map)
        # identify tallest point
        v = self.get_tallest_point(n)    # identify tallest point
        # print "parameter type", MapDecomposer.param.type()
        # print "while", v.get('height'), ">=", MapDecomposer.param.get_parameter("min_height")
        while v.get('height') >= MapDecomposer.param.get_parameter("min_height"):
            p = v.get('position')
            mu = 0
            sigma = 1
            # print "process_map 2:", p, mu, sigma
            for i in range(p - 30, p + 30):
                # print "i =", i, p - 30, p + 30
                if i > 0 or i < len(n):
                    if (n[i] >= 0.9 * n[p]):    # find best fit widest gausian
                        # print "run best fit test", n, i
                        this_sigma = self.best_fit_test(n, i)
                        if this_sigma > sigma:
                            sigma = this_sigma
                            mu = i

            print "appending peak:", item.chr, mu, sigma, v.get('height')
            peaks.append(WaveFileThread.wave(item.chr, mu, sigma, v.get('height')))
            n = MapDecomposer.subtract_gausian(n, v.get('height'), sigma, mu)    # subtract gausian
            v = self.get_tallest_point(n)    # re-calculate tallest point
            print "After subtraction: pos:", v.get("position"), "height:", v.get("height")
            # repeat
        return peaks



    def run(self):
        while True:
            # grabs host from queue
            map_item = self.queue.get()
            # print "run: ", map_item.type()

            print "start process Map", map_item.chr, map_item.start
            peaks = self.process_map(map_item)
            for n in peaks:
                print n.crest, n.sigma, n.chromosome, n.height
            # signals to queue job is done
            self.queue.task_done()


    def start_map_decomposer(self):
        for _x in range(1):
            self.t = MapDecomposer(MapDecomposer.param)
            self.t.setDaemon(True)
            self.t.start()


    def close_map_decomposer(self):
        queue.join()
        self.queue.all_tasks_done
        self.f.close()

        # wait on the queue until everything has been processed
    def add_map(self, map_region, chromosome, start):
        # populate queue with data
        queue.put(MappingItem.item(map_region, chromosome, start))
        # wait on the queue until everything has been processed
