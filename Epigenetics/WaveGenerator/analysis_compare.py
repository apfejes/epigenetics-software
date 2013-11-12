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

    bed = []
    f = open(bedfile, 'r')
    for line in f:
        a = line.split("\t")
        region = {}
        region["chr"] = "chr" + chromosomes[int(a[0].replace("chr", ""))]
        # print "chromosome is: ", region["chr"]
        region["start"] = a[1]
        region["end"] = a[2]
        region["intensity"] = a[3].rstrip()
        bed.append(region)

    maxperbin = 0

    print "Now finding peaks in each region..."
    for i in bed:
        start = int(i["start"])
        end = int(i["end"])
        chrom = str(i["chr"])
        # print "Checking region %s\t%i\t%i" % (chrom, start, end)
        count = 0
        height = 0
        for j in waves:
            if not j["used"] and j["height"] > thresh and j["chr"] == chrom and j["pos"] >= start and j["pos"] <= end:
                # print "Found a peak."
                count += 1
                if count > maxperbin:
                    maxperbin = count
                height += j["height"]
                j["used"] = True
        # print "on line: ", i
        print_queue.put(str(chrom) + "\t" + str(start) + "\t" + str(end) + "\t" + str(i["intensity"]) + "\t" + str(count) + "\t" + str(height))


    # end printing
    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        while print_thread.IS_CLOSED == False:
            print "waiting for print_thread to close"
            time.sleep(1)

    # quick summary statistics
    unassigned = 0
    for i in waves:
        if not i["used"]:
            unassigned += 1
    print "%s waves were unassigned to a BED bin." % unassigned

    print "Max per bin is: ", maxperbin

    counts = [0] * (maxperbin + 1)
    f = open(output + "/comparison.txt", 'r', 0)

    ln = 0
    for line in f:
        ln += 1
        a = line.split("\t")
        print "on line ", ln, " \n line is: ", line, " \nand value is: ", a[4]
        counts[int(a[4])] += 1
    f.close()

    for i in range(0, maxperbin + 1):
        print "# of bins with %s peaks: %s" % (i, counts[i])

if __name__ == "__main__":

    thresh = raw_input("Enter the threshold for peak height: ")
    thresh = float(thresh)
    compare_BED_and_waves("/home/sbrown/Brainstorm/09-08-11_Z_yaf9.bed", "/home/sbrown/Phoebe_CEL/WAVES/09-08-11-Z_yaf9_TRP_IP.normalized.waves", "/home/sbrown/temp", thresh)
    # body of main goes here
    # pass output/path to compare_BED_and_waves
