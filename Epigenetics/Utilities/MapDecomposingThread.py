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
        # height = coverage_map[i]
        # MapDecomposer.printthread.add_string("Starting Best Fit. height " + str(height))
        while True:

            area_over = 0
            area_under = 0
            s = 3 * sigma

            for x in xrange(-s, s):
                if (i + x >= 0 and x < 900 and i + x < len(coverage_map)):
                    expected = height * (MapDecomposer.sigma_height_table[sigma][math.fabs(x)] / MapDecomposer.sigma_height_table[sigma][0])
                    # print "sigma:", sigma, "i,x:", i, x, "(", MapDecomposer.sigma_height_table[sigma][math.fabs(x)], "*", height, "/", MapDecomposer.sigma_height_table[sigma][0], "=", expected, ")"
                    actual = 0
                    if i + x >= 0:
                        actual = coverage_map[i + x]
                    if actual < expected:
                        area_over += (expected - actual)
                        area_under += actual
                    elif actual > expected:
                        area_under += expected
            # MapDecomposer.printthread.add_string("sigma: " + str(sigma) + " over " + str(area_over) + " under " + str(area_under) + " fraction " + str(area_over / area_under))
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
        # print "Processing map starting at " , item.start
        # MapDecomposer.print_queue.put("Processing map starting at " + str(item.start))
        '''tempMatr = [[0 for x_ in xrange(10)] for x_ in xrange(len(item.coverage_map))]    # debugging
        temp_i = 0;    # debugging
        '''

        peaks = []
        n = copy.deepcopy(item.coverage_map)
        '''for i in xrange(len(n)):    # debugging
            # print i
            tempMatr[i][temp_i] = n[i]
        temp_i += 1                    #debugging
        '''

        # identify tallest point
        v = MapDecomposer.get_tallest_point(n)    # identify tallest point
        # first = True    # debugging
        # count = 0    #debugging
        min_height = MapDecomposer.param.get_parameter("min_height")

        lastWave_pos = 0;
        while v.get('height') >= min_height:
            p = v.get('position')
            if lastWave_pos == p:
                break
            else:
                lastWave_pos = p
            '''MapDecomposer.printthread.add_string("running map decomposer with " + str(v.get('height')) +
                                                 ">=" + str(min_height) + " and position " + str(p + item.start))
                                                 #debugging
            '''
            sigma = 1
            for i in range(p - 20, p + 20):
                # MapDecomposer.printthread.add_string("i =" + str(i) + " " + str(p - 30) + " " + str(p + 30))
                if i > 0 and i < len(n):
                    if (n[i] >= 0.9 * n[p]):    # find best fit widest gausian
                        this_sigma = MapDecomposer.best_fit_test(n, i, v.get('height'))
                        if this_sigma > sigma:
                            sigma = this_sigma
                            mu = i
            '''MapDecomposer.print_queue.put("appending peak: " +
                                str(item.chr) + " " + str(item.start + mu) +
                                " " + str(sigma) + " " + str(v.get('height')))
                                '''
            peaks.append(WaveFileThread.wave(item.chr, mu + item.start, sigma, v.get('height')))
            '''MapDecomposer.printthread.add_string(str(n))
            MapDecomposer.printthread.add_string("subtracting: " + str(v.get('height')) + " " + str(sigma) + " " + str(mu))
            '''

            n = MapDecomposer.subtract_gausian(n, v.get('height'), sigma, mu)    # subtract gausian

            '''
            MapDecomposer.printthread.add_string(str(n))
            '''
            v = MapDecomposer.get_tallest_point(n)    # re-calculate tallest point
            '''if count == 4:
                sys.exit()
            count += 1'''
            '''MapDecomposer.printthread.add_string("After subtraction: pos: " +
                                    str(v.get("position")) + " height: " +
                                    str(v.get("height")))
            '''

            '''    
            if first:    #debugging
                filename.write("before:" + MapDecomposer.print_array(item.coverage_map))
                first = False
            filename.write(MapDecomposer.print_array(n))
            '''

            '''if temp_i < 10:         #debugging
                for i in xrange(len(n)):
                    tempMatr[i][temp_i] = n[i]
                temp_i += 1
            '''
            # repeat
            # MapDecomposer.printthread.add_string("Peaks now has " + str(len(peaks)) + " peaks")
        '''the following section is mostly for displaying values for debugging purposes.'''
        '''tempMatr_p = [[0 for _x in xrange(len(peaks))] for _y in xrange(len(item.coverage_map))]
        p_count = 0;
        for p in peaks:
            c_map = MapDecomposer.coverage_from_peak(p.height, p.sigma, p.crest,
                                                     len(n))
            for q in xrange(len(n)):
                tempMatr_p[q][p_count] = c_map[q]
            p_count += 1
        if temp_i > 1:
            filename.write("New peak: " + str(item.chr) + " " + str(item.start) + "\n")
            for q in xrange(len(n)):
                string = []
                for w in xrange(temp_i):
                    m = str(tempMatr[q][w])
                    string.append(m[:m.find(".") + 3] + ",")

                for w in xrange(p_count):
                    m = str(tempMatr_p[q][w])
                    string.append(m[:m.find(".") + 3] + ",")
                filename.write("".join(string) + "\n")
            print "wrote peak to file"
        '''

        '''MapDecomposer.printthread.add_string("Peaks now has " + str(len(peaks)) + " elements")'''
        for n in peaks:
                # MapDecomposer.printthread.add_string("Calling wavefile.add_wave") #debugging
                MapDecomposer.wave_queue.put(n)
        return None


    @staticmethod
    def print_array(n):
        # print "N!:", n
        string = []
        for l in n:
            m = str(l)
            # print "m:", m, " - ", m[:m.find(".") + 3]
            string.append(m[:m.find(".") + 3] + ",")
        return "".join(string) + "last\n"


    def run(self):
        # path = os.path.dirname(os.path.abspath(__file__))
        # path = path.rsplit("/", 1)
        # self.f = open(path[0] + '/testdata/tmp/findwaves.graphs', 'w')
        while True:
            try:
                map_item = queue.get()    # grabs host from queue
                # print "processing", map_item.start
                self.process_map(map_item, self.f)
                # print "processed", map_item.start
            except Queue.Empty:
                if self.end_process:
                    break
                else:
                    continue

    def start_map_decomposer(self):
        pass
            # p = multiprocessing.Process.__init__()
            # (target = worker, args = (nums[chunksize * i:chunksize * (i + 1)], out_q))




            # self.t = MapDecomposer(MapDecomposer.param, MapDecomposer.wavefile,
            #                       MapDecomposer.printthread)
            # self.t.setDaemon(True)
            # self.t.start()


    def close_map_decomposer(self):

        queue.join_thread()
        self.queue.all_tasks_done
        self.end_process = True
        # self.f.close()

        # wait on the queue until everything has been processed
    def add_map(self, map_region, chromosome, start):
        # populate queue with data
        queue.put(MappingItem.Item(map_region, chromosome, start))
        # wait on the queue until everything has been processed
