'''
Created on 2013-11-12

@author: sbrown
'''

import sys
import os
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = _cur_dir
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")

import PrintThread
import multiprocessing


def compare_BED_and_waves(bed, waves, output):
    # body of function goes here

    chromosomes = {1:"I", 2:"II", 3:"III", 4:"IV", 5:"V", 6:"VI", 7:"VII", 8:"VIII", 9:"IX", 10:"X", 11:"XI", 12:"XII", 13:"XIII", 14:"XIV", 15:"XV", 16:"XVI"}


    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, "comparison.txt", True, True)
    waves = []
    f = open(waves, 'r')
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
            waves.append(wave)
    f.close()
    sorted(waves, key = lambda wave: wave["height"], reverse = True)

    bed = []
    f = open(bed, 'r')
    for line in f:
        a = line.split("\t")
        region = {}
        region["chr"] = "chr" + chromosomes[a[0].replace("chr", "")]
        region["start"] = a[1]
        region["end"] = a[2]
        region["intensity"] = a[3]
        bed.append(region)

    # for every line of BED file
        # check if have a line in waves file that is within range
        # write BED file line with count of waves appended
        # also append sum of heights of waves found (measure of how strong the signal is)

if __name__ == "__main__":
    pass
    # body of main goes here
    # pass output/path to compare_BED_and_waves
