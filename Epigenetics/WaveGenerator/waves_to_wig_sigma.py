'''
Created on 2013-11-26

@author: sbrown
'''

import sys
import time
import os
from scipy import stats as scipystats
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")
import multiprocessing
import PrintThread

while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")

import math




def convert_waves_to_wig(wavesfile, output, autothresh):
    # body of function goes here

    waves = []

    print "Reading files..."
    f = open(wavesfile, 'r')
    for line in f:
        if line.startswith("#"):
            continue
        else:
            a = line.split("\t")
            wave = {}
            wave["chr"] = "chr" + a[0].replace("chr", "").upper()
            wave["pos"] = int(a[1])
            wave["stddev"] = int(a[2])
            wave["height"] = float(a[3])
            wave["used"] = False
            waves.append(wave)
    f.close()

    if(autothresh):
        # print "\nNow determining background levels for sigma of peaks"
        bins = 300    # based on max sigma of 300
        counts = [0] * bins
        threshes = [0] * bins
        for i in range(0, bins):
            threshes[i] = (i + 1)
        for i in waves:
            # check all heights to determine background levels
            counts[int(i['stddev'])] += 1    # increment count where height1 is in bin of size 0.1
        # print "counts are: ", counts
        highest = 0
        ind = -1
        for i in range(0, bins):
            if counts[i] > highest:
                highest = counts[i]
                ind = i
        print "Most common sigma:", threshes[ind]
        x = []
        y = []
        for i in range(ind, ind + 5):    # from highest peak forward 5
            x.append(threshes[i])
            y.append(counts[i])
        # print "x is ", x
        # print "y is ", y
        slr = scipystats.linregress(x, y)
        slope = slr[0]
        intercept = slr[1]
        # print "slope: %s and intercept: %s for background peak height" % (slope, intercept)
        # find x-intercept, threshold for noise-signal
        xint = abs(intercept / slope)
        # print "height threshold between noise and signal is ", xint
        thresh = round(xint, 2)
        print "sigma threshold between noise and signal is ", thresh
    else:
        usr_in = raw_input("What would you like to use as the minimum wave sigma? ")
        thresh = int(usr_in)
    # remove waves that don't meet threshold
    waves[:] = [x for x in waves if x['stddev'] > thresh]

    waves.sort(key = lambda x: (x['chr'], x['pos']))    # list sorted by position

    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    # print "printing to: ", output + StringUtils.rreplace(os.path.basename(wavesfile), ".normalized.waves", "_" + str(thresh) + "_summary.txt", 1)
    print_thread = PrintThread.StringWriter(print_queue, output, os.path.basename(wavesfile) + "_" + str(thresh) + ".wig", True, True)

    print_queue.put("track type=wiggle_0 name='" + os.path.basename(wavesfile) + "_WIG'")
    for w in waves:
        start = w['pos'] - 3 * w['stddev']
        offset = 0
        if start < 1:
            offset = 0 - start + 1
            start = start + offset
        print_queue.put("fixedStep chrom=" + w['chr'] + " start=" + str(start) + " step=1")
        # determine max pdf (where x = mu)
        maxpdf = 1.0 / (w['stddev'] * math.sqrt(2.0 * math.pi))
        height = w['height']
        factor = height / maxpdf
        # calculate y-value for pdf curve at each step (+/- 3 stddev from position)
        for i in range(0, (6 * w['stddev'])):
            if i < offset:
                pass
            x = float(i)
            mu = 3.0 * w['stddev']
            exponent = -1 * ((x - mu) * (x - mu) / (2.0 * w['stddev'] * w['stddev']))
            numer = math.exp(exponent)
            denom = w['stddev'] * math.sqrt(2.0 * math.pi)
            y = numer / denom
            print_queue.put(str(round(float(y * factor), 2)))

    # end printing
    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()

    print "Complete."

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wave", help = "The name of the wave file", type = str)
    parser.add_argument("output_path", help = "The location to which the output will be directed", type = str)
    args = parser.parse_args()
    user_in = raw_input("Would you like the program to automatically determine the wave width threshold? (Y/N): ")
    if user_in.lower == "y":
        at = True
    elif at.lower() == "n":
        at = False
    else:
        print "invalid entry."
        sys.exit()
    convert_waves_to_wig(args.wave, args.output_path, at)

