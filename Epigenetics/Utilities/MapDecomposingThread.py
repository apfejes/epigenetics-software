'''
Created on 2013-03-08

@author: afejes
'''

import multiprocessing
import math
import numpy
from Utilities import WaveFileThread, MappingItem
import copy
import os
import Queue

queue = multiprocessing.Queue(400)    # don't let the main process get too far ahead
max_sigma = 300


class MapDecomposer(multiprocessing.Process):

    f = None
    t = None
    param = None
    sigma_height_table = None
    print_queue = None
    wave_queue = None

    def __init__(self, param, wave_queue, print_queue, name):
        self._parent_pid = os.getpid()
        self._name = name
        self._popen = None
        self._daemonic = True
        self.end_process = False
        if (MapDecomposer.wave_queue == None):
            MapDecomposer.wave_queue = wave_queue
        self.queue = queue
        if (MapDecomposer.print_queue == None):
            MapDecomposer.print_queue = print_queue
        if (MapDecomposer.param == None):
            MapDecomposer.param = param
        if (MapDecomposer.sigma_height_table == None):
            MapDecomposer.sigma_height_table = numpy.ndarray((max_sigma, 3 * max_sigma))
            '''first variable is the sigma, second is the number of spaces away 
            from the centre of the peak'''
            for i in xrange(1, max_sigma):    # sigma - which can't be = to zero
                for j in xrange(1, 3 * max_sigma):    # distance from peak
                    MapDecomposer.sigma_height_table[i][j] = \
                                MapDecomposer.gausian_value_at_x(i, 0, j)
                MapDecomposer.sigma_height_table[i][0] = \
                            MapDecomposer.gausian_value_at_peak(i)

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
        '''use this to figure out this the max height of the gausian. The 
        e^whatever turns into e^0 = 1.'''
        f = 1.0 / (sigma * math.sqrt(2.0 * math.pi))
        return f

    @staticmethod
    def subtract_gausian(coverage_map, height, sigma, mu):
        max_ht = MapDecomposer.gausian_value_at_peak(sigma)
        s = sigma * 3
        for i in range(-s, s):
            if (i + mu >= 0 and i + mu < len(coverage_map)):
                coverage_map[i + mu] -= (height * \
                        (MapDecomposer.sigma_height_table[sigma][math.fabs(i)] \
                         / max_ht))
        return coverage_map

    @staticmethod
    def coverage_from_peak(height, sigma, mu, length):
        coverage_map = [0] * length
        max_ht = MapDecomposer.gausian_value_at_peak(sigma)
        s = sigma * 3
        for i in range(-s, s):
            if (i + mu >= 0 and i + mu < len(coverage_map)):
                coverage_map[i + mu] = (height * \
                        (MapDecomposer.sigma_height_table[sigma][math.fabs(i)] \
                         / max_ht))
        return coverage_map


    @staticmethod
    def best_fit_test(coverage_map, i, height):
        '''i is the position to test for the best fit in the coverage_map.'''
        sigma = 1
        while True:
            area_over = 0
            area_under = 0
            s = 3 * sigma
            for x in xrange(-s, s):
                if (i + x >= 0 and x < 900 and i + x < len(coverage_map)):
                    expected = height * (MapDecomposer.sigma_height_table[sigma][math.fabs(x)] / MapDecomposer.sigma_height_table[sigma][0])
                    actual = 0
                    if i + x >= 0:
                        actual = coverage_map[i + x]
                    if actual < expected:
                        area_over += (expected - actual)
                        area_under += actual
                    elif actual > expected:
                        area_under += expected
            if (area_over > (1.0 / sigma) * area_under):
                return sigma - 1;
            if sigma >= 299:
                return sigma - 1
            sigma += 1
        return sigma - 1    # once it breaks, it has gone one sigma further than it should have, so subtract one.

    @staticmethod
    def process_map(item, filename):
        '''takes in a coverage map object and begins the process of identifying
         the normal curves that best fit the map.'''
        peaks = []
        n = copy.deepcopy(item.coverage_map)
        v = MapDecomposer.get_tallest_point(n)    # identify tallest point
        min_height = MapDecomposer.param.get_parameter("min_height")
        lastWave_pos = 0;
        while v.get('height') >= min_height:
            p = v.get('position')
            if lastWave_pos == p:
                break
            else:
                lastWave_pos = p
            sigma = 1
            for i in range(p - 20, p + 20):
                if i > 0 and i < len(n):
                    if (n[i] >= 0.9 * n[p]):    # find best fit widest gausian
                        this_sigma = MapDecomposer.best_fit_test(n, i, v.get('height'))
                        if this_sigma > sigma:
                            sigma = this_sigma
                            mu = i
            peaks.append(WaveFileThread.wave(item.chr, mu + item.start, sigma, v.get('height')))
            n = MapDecomposer.subtract_gausian(n, v.get('height'), sigma, mu)    # subtract gausian
            v = MapDecomposer.get_tallest_point(n)    # re-calculate tallest point
            # repeat
        for n in peaks:
                MapDecomposer.wave_queue.put(n)
        return None


    @staticmethod
    def print_array(n):
        string = []
        for l in n:
            m = str(l)
            string.append(m[:m.find(".") + 3] + ",")
        return "".join(string) + "last\n"


    def run(self):
        while True:
            try:
                map_item = queue.get()    # grabs host from queue
                self.process_map(map_item, self.f)
            except Queue.Empty:
                if self.end_process:
                    break
                else:
                    continue

    def close_map_decomposer(self):
        queue.join_thread()
        self.queue.all_tasks_done
        self.end_process = True


    def add_map(self, map_region, chromosome, start):
        '''populate queue with data'''
        queue.put(MappingItem.Item(map_region, chromosome, start))
        # wait on the queue until everything has been processed
