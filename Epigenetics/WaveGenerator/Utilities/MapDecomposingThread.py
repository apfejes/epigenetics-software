'''
Created on 2013-03-08

@author: afejes
'''

import multiprocessing
import math
import numpy
from Utilities import WaveFileThread, MappingItem
import os
import Queue
import sys

    # don't let the main process get too far ahead
max_sigma = 300
END_PROCESSES = False

class MapDecomposer(multiprocessing.Process):

    f = None
    t = None
    PARAM = None
    sigma_height_table = None
    print_queue = None
    map_queue = None
    wave_queue = None

    def __init__(self, PARAM, wave_queue, print_queue, map_queue, name):
        self._parent_pid = os.getpid()
        self._name = name
        self._popen = None
        self._daemonic = True

        if (MapDecomposer.wave_queue == None):
            MapDecomposer.wave_queue = wave_queue
        if (MapDecomposer.map_queue == None):
            MapDecomposer.map_queue = map_queue
        if (MapDecomposer.print_queue == None):
            MapDecomposer.print_queue = print_queue
        if (MapDecomposer.PARAM == None):
            MapDecomposer.PARAM = PARAM
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
    def best_fit_slow(coverage_map, i, height):
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
                return sigma - 1
            if sigma >= 299:
                return sigma - 1
            sigma += 1
        return sigma - 1    # once it breaks, it has gone one sigma further than it should have, so subtract one.

    @staticmethod
    def best_fit_newton(coverage_map, i, height):
        '''i is the position to test for the best fit in the coverage_map.'''
        low_sigma = 1
        high_sigma = max_sigma - 1
        if MapDecomposer.sigma_test(coverage_map, max_sigma - 1, i, height):    # still too high
            sys.exit("max sigma not set high enough - halting")
        sigma = int((high_sigma - low_sigma) / 2.0)
        while low_sigma != high_sigma - 1:
            if not MapDecomposer.sigma_test(coverage_map, sigma, i, height):    # still too high
                high_sigma = sigma
            else:    # still too low
                low_sigma = sigma
            sigma = ((high_sigma - low_sigma) / 2) + low_sigma
        return low_sigma


    @staticmethod
    def sigma_test(coverage_map, sigma, i, height):
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
            return False
        if sigma >= 299:
            return False
        return True


    @staticmethod
    def process_map(item, filename):
        '''takes in a coverage map object and begins the process of identifying
         the normal curves that best fit the map.'''
        peaks = []
        n = list(item.coverage_map)    # creates a new, independent list
        v = MapDecomposer.get_tallest_point(n)    # identify tallest point
        highest_point = v.get('height')
        cur_height = v.get('height')
        min_height = MapDecomposer.PARAM.get_parameter("min_height")
        number_waves = MapDecomposer.PARAM.get_parameter("number_waves")

        lastWave_pos = 0
        if number_waves:
            wave_number = 1
        else:
            wave_number = None
        while cur_height >= 0.2 * highest_point and cur_height >= min_height:    # TODO: Should be replaced with percentage of maxheight.
            p = v.get('position')
            if lastWave_pos == p:
                break
            else:
                lastWave_pos = p
            sigma = 0
            processed = False
            for i in range(p - 15, p + 15):
                if i > 0 and i < len(n):
                    if (n[i] >= 0.9 * cur_height):    # find best fit widest gausian
                        this_sigma = MapDecomposer.best_fit_newton(n, i, cur_height)
                        if this_sigma > sigma:
                            sigma = this_sigma
                            mu = i
                            processed = True
            if not processed:
                MapDecomposer.print_queue.put("A region was not processed")
                MapDecomposer.print_queue.put("region start position: " + str(item.start))
                MapDecomposer.print_queue.put("i was from p " + str(p) + ", giving " + str(p - 15) + " to " + str(p + 15))
                MapDecomposer.print_queue.put("len(n) is  " + str(len(n)))
                MapDecomposer.print_queue.put("height n[p] is  " + str(n[p]))
                str_list = []
                for i in range (p - 15, p + 15):
                    str_list.append(str(n[i]))
                    str_list.append(" ")
                MapDecomposer.print_queue.put("".join(str_list))
                return None

            peaks.append(WaveFileThread.wave(item.chr, mu + item.start, sigma, cur_height, wave_number))
            n = MapDecomposer.subtract_gausian(n, cur_height, sigma, mu)    # subtract gausian
            v = MapDecomposer.get_tallest_point(n)    # re-calculate tallest point
            cur_height = v.get('height')
            if number_waves:
                wave_number += 1
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
                map_item = MapDecomposer.map_queue.get()    # grabs host from queue
                self.process_map(map_item, self.f)
                # MapDecomposer.map_queue.task_done()
            except Queue.Empty:
                if END_PROCESSES:
                    self.print_queue.put("thread received signal to quit")
                    break
                else:
                    continue

    # def close_map_decomposer(self):
    #    '''instructions to close out the thread and end the process.'''
    #    queue.join_thread()
    #    self.end_process = True

    @staticmethod
    def add_map(map_region, chromosome, start):
        '''populate queue with data'''
        MapDecomposer.map_queue.put(MappingItem.Item(map_region, chromosome, start))
        # wait on the queue until everything has been processed
