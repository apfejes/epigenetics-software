'''
Created on 2013-11-22

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




def convert_waves_to_bed(wavesfile, output, autothresh):
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
            wave["height"] = float(a[2])
            wave["stddev"] = int(a[3])
            wave["used"] = False
            waves.append(wave)
    f.close()

    if(autothresh):
        # print "\nNow determining background levels for height of peaks"
        bins = 70    # based on max peak height of 7
        counts = [0] * bins
        thresh = [0] * bins
        for i in range(0, bins):
            thresh[i] = (i + 1) * 0.1
        for i in waves:
            # check all heights to determine background levels
            counts[int(i['height'] / 0.1)] += 1    # increment count where height1 is in bin of size 0.1
        # print "counts are: ", counts
        x = []
        y = []
        for i in range(10, 15):    # (0 to 9 correspond to heights 0 to 0.9, do not have)
            x.append(thresh[i])
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
    else:
        usr_in = raw_input("What would you like to use as the minimum wave height? ")
        thresh = float(usr_in)
    # remove waves that don't meet threshold
    waves[:] = [x for x in waves if x['height'] > thresh]

    waves.sort(key = lambda x: (x['chr'], x['pos']))    # list sorted by position

    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    # print "printing to: ", output + StringUtils.rreplace(os.path.basename(wavesfile), ".normalized.waves", "_" + str(thresh) + "_summary.txt", 1)
    print_thread = PrintThread.StringWriter(print_queue, output, os.path.basename(wavesfile) + "_" + str(thresh) + ".bed", True, True)

    maxscore = 1000    # for shading regions in UCSC
    print_queue.put("track name=" + os.path.basename(wavesfile) + "_BED useScore=1")
    for w in waves:
        print_queue.put(w['chr'] + "\t" + str(w['pos'] - 3 * w['stddev']) + "\t" + str(w['pos'] + 3 * w['stddev']) + "\t\t" + str(w['height'] / 7 * maxscore))

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
    user_in = raw_input("Would you like the program to automatically determine the wave height threshold? (Y/N): ")
    if user_in.lower() == "y":
        at = True
    elif user_in.lower() == "n":
        at = False
    else:
        print "invalid entry."
        sys.exit()
    convert_waves_to_bed(args.wave, args.output_path, at)

