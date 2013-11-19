'''
Created on 2013-11-12

@author: sbrown
'''

import sys
import time
import os

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")
import multiprocessing
import PrintThread



def compare_BED_and_waves(bedfile, wavesfile, output, thresh):
    # body of function goes here

    chromosomes = {1:"I", 2:"II", 3:"III", 4:"IV", 5:"V", 6:"VI", 7:"VII", 8:"VIII", 9:"IX", 10:"X", 11:"XI", 12:"XII", 13:"XIII", 14:"XIV", 15:"XV", 16:"XVI"}


    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, "comparison.txt", True, True)
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
    waves[:] = [x for x in waves if x['height'] > thresh]

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

    '''
    for i in bed:
        start = int(i["start"])
        end = int(i["end"])
        chrom = str(i["chr"])
        # print "Checking region %s\t%i\t%i" % (chrom, start, end)
        count = 0
        height = 0
        for j in waves:
            # print "wave pos: ", j['pos']
            if j['pos'] > end:
                # print "BREAKING!"
                break
            if not j["used"] and j["chr"] == chrom and j["pos"] >= start and j["pos"] <= end:
                # print "Found a peak."
                count += 1
                if count > maxperbin:
                    maxperbin = count
                height += j["height"]
                j["used"] = True
        # print "on line: ", i
        print_queue.put(str(chrom) + "\t" + str(start) + "\t" + str(end) + "\t" + str(i["intensity"]) + "\t" + str(count) + "\t" + str(height))
    '''

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

    # quick summary statistics
    unassigned = 0
    for i in waves:
        if not i["used"]:
            unassigned += 1
    # print "%s waves were unassigned to a BED bin." % unassigned

    print "Max per bin is: ", maxperbin

    counts = [0] * (maxperbin + 1)
    f = open(output + "/comparison.txt", 'r', 0)

    ln = 0
    for line in f:
        ln += 1
        a = line.split("\t")
        # print "on line ", ln, " \n line is: ", line, " \nand value is: ", a[4]
        counts[int(a[4])] += 1
    f.close()
    print "%s waves were unassigned to a BED bin." % unassigned
    for i in range(0, maxperbin + 1):
        print "# of bins with %s waves: \t%s" % (i, counts[i])

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print ("This program requires the name of the ChIP-chip bed file, ChIP-chip waves file, and output/path")
        print" eg. python analysis_compare.py /directory/database.conf directory/output/ yeast_epigenetics"
        sys.exit()
    bed = sys.argv[1]
    wave = sys.argv[2]
    out = sys.argv[3]
    thresh = raw_input("Enter the threshold for peak height: ")
    thresh = float(thresh)
    compare_BED_and_waves(bed, wave, out, thresh)

