'''
Created on 2013-03-08

@author: afejes
'''

import multiprocessing
import math
# import numpy
import WaveFileThread
import os
import Queue
import cProfile

END_PROCESS = None

    # don't let the main process get too far ahead
max_sigma = 300

class MapDecomposer(multiprocessing.Process):

    f = None
    t = None
    PARAM = None
    print_queue = None
    wave_queue = None

    def __init__(self, PARAM, wave_queue, print_queue, map_queue, name):
        self._parent_pid = os.getpid()
        self._name = name
        self._popen = None
        self._daemonic = True
        self.map_queue = map_queue
        self.sigma_height_table = [[0 for i in range(3 * max_sigma)] for j in range(max_sigma)]

        # numpy.ndarray((max_sigma, 3 * max_sigma))

        if (MapDecomposer.wave_queue is None):
            MapDecomposer.wave_queue = wave_queue
        if (MapDecomposer.print_queue is None):
            MapDecomposer.print_queue = print_queue
        if (MapDecomposer.PARAM is None):
            MapDecomposer.PARAM = PARAM

        '''first variable is the sigma, second is the number of spaces away 
            from the centre of the peak'''
        for i in xrange(1, max_sigma):    # sigma - which can't be = to zero
            for j in xrange(1, 3 * max_sigma):    # distance from peak
                self.sigma_height_table[i][j] = \
                            MapDecomposer.gausian_value_at_x(i, 0, j)
            self.sigma_height_table[i][0] = \
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

    def subtract_gausian(self, coverage_map, height, sigma, mu):
        max_ht = MapDecomposer.gausian_value_at_peak(sigma)
        s = sigma * 3
        for i in range(-s, s):
            if (i + mu >= 0 and i + mu < len(coverage_map)):
                coverage_map[i + mu] -= (height * \
                        (self.sigma_height_table[sigma][abs(i)] / max_ht))
        return coverage_map

    def coverage_from_peak(self, height, sigma, mu, length):
        coverage_map = [0] * length
        max_ht = MapDecomposer.gausian_value_at_peak(sigma)
        s = sigma * 3
        for i in range(-s, s):
            if (i + mu >= 0 and i + mu < len(coverage_map)):
                coverage_map[i + mu] = (height * \
                        (self.sigma_height_table[sigma][abs(i)] / max_ht))
        return coverage_map



    def best_fit_newton(self, coverage_map, i, height):
        '''i is the position to test for the best fit in the coverage_map.'''
        low_sigma = 1
        high_sigma = max_sigma - 1
#        if MapDecomposer.sigma_test(coverage_map, max_sigma - 1, i, height):    # still too high
#            sys.exit("max sigma not set high enough - halting")
        sigma = int((high_sigma - low_sigma) / 2.0)
        while low_sigma != high_sigma - 1:
            if not self.sigma_test(coverage_map, sigma, i, height):    # still too high
                high_sigma = sigma
            else:    # still too low
                low_sigma = sigma
            sigma = ((high_sigma - low_sigma) / 2) + low_sigma
        return low_sigma


    def sigma_test(self, coverage_map, sigma, i, height):
        area_over = 0
        area_under = 0
        s = 3 * sigma
        base = self.sigma_height_table[sigma][0]
        map_len = len(coverage_map)
        for x in xrange(-s, s):
            t = i + x
            if (t >= 0 and x < 900 and t < map_len):
                expected = height * (self.sigma_height_table[sigma][abs(x)] / base)
                actual = coverage_map[t]
                if actual < expected:
                    area_over += (expected - actual)
                    area_under += actual
                elif actual > expected:
                    area_under += expected
        if area_over > (area_under / sigma):
            return False
        if sigma >= 299:
            return False
        return True

    def to_be_tested(self, sample):
        sample.sort()
        to_be_tested = set()
        for i in range(len(sample) - 1):
            if i == 0 and sample[i][1] > sample[i + 1][1]:
                if sample[i + 1][0] - sample[i][0] > 1:
                    t = int((sample[i + 1][0] - sample[i][0]) / 2) + sample[i][0]
                    if t not in to_be_tested:
                        to_be_tested.add(t)
            elif i == len(sample) and sample[i][1] > sample[i - 1][1]:
                if sample[i][0] - sample[i - 1][0] > 1:
                    t = int((sample[i][0] - sample[i - 1][0]) / 2) + sample[i - 1][0]
                    if t not in to_be_tested:
                        to_be_tested.add(t)
            elif sample[i][1] >= sample[i - 1][1] and sample[i][1] >= sample[i + 1][1]:
                if sample[i + 1][0] - sample[i][0] > 1:
                    t = int((sample[i + 1][0] - sample[i][0]) / 2) + sample[i][0]
                    if t not in to_be_tested:
                        to_be_tested.add(t)
                if sample[i][0] - sample[i - 1][0] > 1:
                    t = int((sample[i][0] - sample[i - 1][0]) / 2) + sample[i - 1][0]
                    if t not in to_be_tested:
                        to_be_tested.add(t)
        return to_be_tested

    def get_mu(self, testing):
        start = 0
        end = 0
        height = 0    # this is actually the best sigma value
        for t in testing:
            if t[1] > height:
                start = t[0]
                end = 0
                height = t[1]
            elif t[1] == height:
                end = t[0]
        if not end == 0:
            return (int((end - start) / 2) + start, height)
        else :
            return (start, height)

    def process_map(self, item, filename):
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
        # print("heights %f, %f, %f (cur, highest, min)" % (cur_height, highest_point, min_height))
        while cur_height >= 0.2 * highest_point and cur_height >= min_height:

            p = v.get('position')
            if lastWave_pos == p:
                break
            else:
                lastWave_pos = p
            width = 40    # for now, must be divisible by 10
            tested = []
            for i in range(p - width, p + width, 10):
                if i > 0 and i < len(n):
                    this_sigma = self.best_fit_newton(n, i, cur_height)
                    tested.append((i - (p - width), this_sigma))
            tbt = self.to_be_tested(tested)
            while len(tbt) > 0:
                for t in tbt:
                    tested.append((t, self.best_fit_newton(n, (t + (p - width)), cur_height)))
                tbt = []
                tbt = self.to_be_tested(tested)
            best = self.get_mu(tested)    # returns mu and sigma.
            mu = best[0] + (p - width)
            sigma = best[1]
            peaks.append(WaveFileThread.wave(item.chr, mu + item.start, sigma, cur_height, wave_number))
            # print "appended a wave"
            n = self.subtract_gausian(n, cur_height, sigma, mu)    # subtract gausian
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


    def run_wrapper(self, *args):
        self.print_queue.put("profiling started")
        cProfile.runctx("self.run(args)", globals(), locals())
        self.print_queue.put("finished profiling")

    def run(self, *args):
        while True:
            try:
                map_item = self.map_queue.get(True)    # grabs map from queue\
                # print "got an item."
                if map_item is None:
                    break
                self.process_map(map_item, self.f)
                # print "map processed"
            except KeyboardInterrupt:
                self.print_queue.put("ignoring Ctrl-C for worker process")
            except Queue.Empty:
                pass    # ignore this error.



    # def close_map_decomposer(self):
    #    '''instructions to close out the thread and end the process.'''
    #    queue.join_thread()
    #    self.end_process = True

    def name(self):
        return self.name
