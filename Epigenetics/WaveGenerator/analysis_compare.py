'''
Created on 2013-11-12

@author: sbrown
'''

import sys
import time
import os
from scipy import stats as scipystats

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
import StringUtils



def compare_BED_and_waves(bedfile, wavesfile, output, autothresh, heisig):
    # body of function goes here

    chromosomes = {1:"I", 2:"II", 3:"III", 4:"IV", 5:"V", 6:"VI", 7:"VII", 8:"VIII", 9:"IX", 10:"X", 11:"XI", 12:"XII", 13:"XIII", 14:"XIV", 15:"XV", 16:"XVI"}

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
        if(heisig):
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
            print "height threshold between noise and signal is ", xint
            thresh = round(xint, 2)
        else:
            # determine threshold for sigma
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
            thresh = threshes[ind]
            print "sigma threshold between noise and signal is ", thresh
    else:
        if(heisig):
            usr_in = raw_input("What would you like to use as the minimum wave height? ")
            thresh = float(usr_in)
        else:
            usr_in = raw_input("What would you like to use as the minimum wave sigma? ")
            thresh = int(usr_in)
    # remove waves that don't meet threshold
    if(heisig):
        waves[:] = [x for x in waves if x['height'] > thresh]
    else:
        waves[:] = [x for x in waves if x['stddev'] > thresh]

    waves.sort(key = lambda x: (x['chr'], x['pos']))    # list sorted by position

    bed = []
    f = open(bedfile, 'r')
    for line in f:
        a = line.split("\t")
        region = {}
        region["chr"] = "chr" + chromosomes[int(a[0].replace("chr", ""))]
        # print "chromosome is: ", region["chr"]
        region["start"] = int(a[1])
        region["end"] = int(a[2])
        region["intensity"] = float(a[3].rstrip())
        bed.append(region)

    bed.sort(key = lambda x: (x['chr'], x['start']))

    maxperbin = 0

    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, StringUtils.rreplace(os.path.basename(bedfile), ".bed", "_" + str(thresh) + "_summary.txt", 1), True, True)

    print "Now finding peaks in each region..."
    w = 0
    b = 0
    count = 0
    height = 0

    while b < len(bed) and w < len(waves):
        if(waves[w]['chr'] == bed[b]['chr'] and waves[w]['pos'] >= bed[b]['start'] and waves[w]['pos'] <= bed[b]['end']):
            # print "found a wave in bin ", b
            count += 1
            if count > maxperbin:
                maxperbin = count
            height += waves[w]['height']
            waves[w]['used'] = True
            w += 1
        elif waves[w]['chr'] > bed[b]['chr'] or (waves[w]['pos'] > bed[b]['end'] and waves[w]['chr'] == bed[b]['chr']):
            # wave is past bin, move to next bin
            # write to file
            # print "b: %i, w: %i, wave is AFTER, start: %s, end: %s, pos: %s, %s %s" % (b, w, bed[b]['start'], bed[b]['end'], waves[w]['pos'], bed[b]['chr'], waves[w]['chr'])
            print_queue.put(bed[b]['chr'] + "\t" + str(bed[b]['start']) + "\t" + str(bed[b]['end']) + "\t" + str(bed[b]["intensity"]) + "\t" + str(count) + "\t" + str(height))
            b += 1
            count = 0
            height = 0
        else:
            # wave is before bin
            # print "b: %i, w: %i, wave is BEFORE, start: %s, end: %s, pos: %s, %s %s" % (b, w, bed[b]['start'], bed[b]['end'], waves[w]['pos'], bed[b]['chr'], waves[w]['chr'])
            w += 1

    while b < len(bed):
        # if ended because got to end of waves
        # need to write statistics for remaining bins
        # print "filling in remaining bins with 0s"
        start = bed[b]["start"]
        end = bed[b]["end"]
        chrom = bed[b]["chr"]

        count = 0
        height = 0

        print_queue.put(str(chrom) + "\t" + str(start) + "\t" + str(end) + "\t" + str(bed[b]["intensity"]) + "\t" + str(count) + "\t" + str(height))
        b += 1

    # end printing
    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()
        # while not print_thread.is_closed():
        #    print "waiting for print_thread to close ", print_queue.qsize(), " ", print_thread.is_closed(), " ", print_thread.END_PROCESSES
        #    time.sleep(1)


    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, StringUtils.rreplace(os.path.basename(bedfile), ".bed", "_" + str(thresh) + "_counts.txt", 1), True, True)


    # quick summary statistics
    print_queue.put("nwaves\tnbins\tavgBinSize")
    unassigned = 0
    un_height = 0
    for i in waves:
        if not i["used"]:
            unassigned += 1
            un_height += i["height"]
            # print i['height']

    # for each bin of height 0.5, determine % of waves not mapped
    total = [0] * 13
    unmap = [0] * 13
    for i in waves:
        total[int(i['height'] / 0.5) - 2] += 1    # TODO: this is almost certainly wrong!
        if not i['used']:
            unmap[int(i['height'] / 0.5) - 2] += 1    # TODO: most certainly wrong.
    # TODO: Print these values in some meaningful way.
    prop = [0.0] * 13
    for i in range(0, len(prop)):
        if total[i] != 0:
            prop[i] = float(unmap[i]) / float(total[i])
        else:
            prop[i] = 0
    print "Proportions of unused waves in each bin:"
    print "[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]"
    print unmap
    print total
    print prop

    # print "%s waves were unassigned to a BED bin." % unassigned

    print "Max per bin is:", maxperbin
    print "Height threshold applied to waves:", thresh

    counts = [0] * (maxperbin + 1)
    # sizes = [[]] * (maxperbin + 1)
    sizes = [[] for x in range(0, maxperbin + 1)]
    f = open(output + StringUtils.rreplace(os.path.basename(bedfile), ".bed", "_" + str(thresh) + "_summary.txt", 1), 'r', 0)

    ln = 0
    for line in f:
        ln += 1
        a = line.split("\t")
        # print "on line ", ln, " \n line is: ", line, " \nand value is: ", a[4]
        counts[int(a[4])] += 1
        sizes[int(a[4])].append(int(a[2]) - int(a[1]))
    f.close()
    print "%s waves were unassigned to a BED bin." % unassigned
    print "Average height of waves not part of a bin:", (un_height / unassigned)
    print_queue.put(str(unassigned) + "\t0\t0")
    for i in range(0, maxperbin + 1):
        tot = 0
        # print len(sizes[i])
        for j in range(0, len(sizes[i])):
            tot += sizes[i][j]
            # print "size is: ", sizes[i][j]
        if len(sizes[i]) != 0:
            avg = float(tot) / len(sizes[i])
        else:
            avg = 0
        print "# of bins with %s waves: %s, and average size is: %s" % (i, counts[i], avg)
        print_queue.put(str(i) + "\t" + str(counts[i]) + "\t" + str(avg))

    # end printing
    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print ("This program requires the name of the ChIP-chip bed file, ChIP-chip waves file, and output/path")
        print" eg. python analysis_compare.py /directory/database.conf directory/output/ yeast_epigenetics"
        sys.exit()
    bed = sys.argv[1]
    wave = sys.argv[2]
    out = sys.argv[3]
    sh = raw_input("Would you like to use a wave height, or wave sigma threshold? [h]eight or [s]igma: ")
    if sh == "h" or sh == "H":
        sh = True
    elif sh == "s" or sh == "S":
        sh = False
    else:
        print "invalid entry."
        sys.exit()
    at = raw_input("Would you like the program to automatically determine the threshold? (Y/N): ")
    if at == "Y" or at == "y":
        at = True
    elif at == "N" or at == "n":
        at = False
    else:
        print "invalid entry."
        sys.exit()
    compare_BED_and_waves(bed, wave, out, at, sh)

