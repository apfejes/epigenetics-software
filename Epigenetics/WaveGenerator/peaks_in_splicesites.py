'''
Created on 2013-12-04

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



def find_waves_in_spliced_genes(splicefile, wavesfile, output, autothresh, heisig, thresh):
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

    # remove waves that don't meet threshold
    if(heisig):
        waves[:] = [x for x in waves if x['height'] > thresh]
    else:
        waves[:] = [x for x in waves if x['stddev'] > thresh]

    waves.sort(key = lambda x: (x['chr'], x['pos']))    # list sorted by position

    splice = []
    f = open(splicefile, 'r')
    for line in f:
        a = line.split("\t")
        region = {}
        region["gene"] = a[0]
        region["chr"] = "chr" + chromosomes[int(a[1])]
        if int(a[2]) == 1:    # forward
            # promoter
            region["p1"] = int(a[3]) - 301    # p1 is left boundary of promoter
            region["p2"] = int(a[3]) - 1    # p2 is right boundary of promoter
            # exon1
            region["e11"] = int(a[3])    # e11 is left boundary of exon1
            region["e12"] = int(a[4])    # e12 us right boundary of exon1
            # intron
            region["i1"] = int(a[5])
            region["i2"] = int(a[6])
            # exon2
            region["e21"] = int(a[7])
            region["e22"] = int(a[8])
            # 3' UTR
            region["u1"] = int(a[8]) + 1    # 3'UTR
            region["u2"] = int(a[8]) + 301
        else:    # reverse
            # promoter
            region["p1"] = int(a[4]) - 301
            region["p2"] = int(a[4]) - 1
            # exon1
            region["e11"] = int(a[4])
            region["e12"] = int(a[3])
            # intron
            region["i1"] = int(a[6])
            region["i2"] = int(a[5])
            # exon2
            region["e21"] = int(a[8])
            region["e22"] = int(a[7])
            # 3' UTR
            region["u1"] = int(a[7]) + 1
            region["u2"] = int(a[7]) + 301
        # counts in each region
        region['p'] = 0
        region['e1'] = 0
        region['i'] = 0
        region['e2'] = 0
        region['u'] = 0

        # splice site regions (+/- 100 bp)
        region['pe11'] = region['e11'] - 99    # promoter to exon1 left boundary
        region['pe12'] = region['e11'] + 101    # promoter to exon1 right boundary
        region['e1i1'] = region['i1'] - 99
        region['e1i2'] = region['i1'] + 101
        region['ie21'] = region['e21'] - 99
        region['ie22'] = region['e21'] + 101
        region['e2u1'] = region['u1'] - 99
        region['e2u2'] = region['u1'] + 101
        # splice site counts
        region['pe1'] = 0
        region['e1i'] = 0
        region['ie2'] = 0
        region['e2u'] = 0
        splice.append(region)

    splice.sort(key = lambda x: (x['chr'], x['p1']))



    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, StringUtils.rreplace(os.path.basename(wavesfile), ".normalized.waves", "_" + str(thresh) + "_splice_summary.txt", 1), True, True)
    # print header
    print_queue.put("gene\tchr\tp1\tp2\te11\te12\ti1\ti2\te21\te22\tu1\tu2\tp\tpe1\te1\te1i\ti\tie2\te2\te2u\tu")
    print "Now finding peaks in each region..."
    w = 0
    b = 0


    while b < len(splice) and w < len(waves):
        if(waves[w]['chr'] == splice[b]['chr'] and (waves[w]['pos'] + 1 * waves[w]['stddev']) >= splice[b]['p1'] and (waves[w]['pos'] - 1 * waves[w]['stddev']) <= splice[b]['u2']):
            # print "found a wave in gene ", splice["gene"]
            # find which segment of gene it is present in
            # only use standard deviation threshold when at beginning of promoter and end of UTR
            if (waves[w]['pos'] + 1 * waves[w]['stddev']) >= splice[b]['p1'] and waves[w]['pos'] <= splice[b]['p2']:
                splice[b]['p'] += 1.0 / (splice[b]['p2'] - splice[b]['p1'])
            elif waves[w]['pos'] >= splice[b]['e11'] and waves[w]['pos'] <= splice[b]['e12']:
                splice[b]['e1'] += 1.0 / (splice[b]['e12'] - splice[b]['e11'])
            elif waves[w]['pos'] >= splice[b]['i1'] and waves[w]['pos'] <= splice[b]['i2']:
                splice[b]['i'] += 1.0 / (splice[b]['i2'] - splice[b]['i1'])
            elif waves[w]['pos'] >= splice[b]['e21'] and waves[w]['pos'] <= splice[b]['e22']:
                splice[b]['e2'] += 1.0 / (splice[b]['e22'] - splice[b]['e21'])
            elif waves[w]['pos'] >= splice[b]['u1'] and (waves[w]['pos'] - 1 * waves[w]['stddev']) <= splice[b]['u2']:
                splice[b]['u'] += 1.0 / (splice[b]['u2'] - splice[b]['u1'])

            if waves[w]['pos'] >= splice[b]['pe11'] and waves[w]['pos'] <= splice[b]['pe12']:
                splice[b]['pe1'] += 1.0 / (splice[b]['pe12'] - splice[b]['pe11'])
            elif waves[w]['pos'] >= splice[b]['e1i1'] and waves[w]['pos'] <= splice[b]['e1i2']:
                splice[b]['e1i'] += 1.0 / (splice[b]['e1i2'] - splice[b]['e1i1'])
            elif waves[w]['pos'] >= splice[b]['ie21'] and waves[w]['pos'] <= splice[b]['ie22']:
                splice[b]['ie2'] += 1.0 / (splice[b]['ie22'] - splice[b]['ie21'])
            elif waves[w]['pos'] >= splice[b]['e2u1'] and waves[w]['pos'] <= splice[b]['e2u2']:
                splice[b]['e2u'] += 1.0 / (splice[b]['e2u2'] - splice[b]['e2u1'])
            waves[w]['used'] = True
            w += 1
        elif waves[w]['chr'] > splice[b]['chr'] or ((waves[w]['pos'] - 1 * waves[w]['stddev']) > splice[b]['u2'] and waves[w]['chr'] == splice[b]['chr']):
            # wave is past bin, move to next bin
            # write to file
            # print "b: %i, w: %i, wave is AFTER, start: %s, end: %s, pos: %s, %s %s" % (b, w, splice[b]['start'], splice[b]['end'], waves[w]['pos'], splice[b]['chr'], waves[w]['chr'])
            print_queue.put(splice[b]['gene'] + "\t" + splice[b]['chr'] + "\t" + \
                            str(splice[b]['p1']) + "\t" + str(splice[b]['p2']) + "\t" + \
                            str(splice[b]['e11']) + "\t" + str(splice[b]['e12']) + "\t" + \
                            str(splice[b]['i1']) + "\t" + str(splice[b]['i2']) + "\t" + \
                            str(splice[b]['e21']) + "\t" + str(splice[b]['e22']) + "\t" + \
                            str(splice[b]['u1']) + "\t" + str(splice[b]['u2']) + "\t" + \
                            str(splice[b]['p']) + "\t" + str(splice[b]['pe1']) + "\t" + \
                            str(splice[b]['e1']) + "\t" + str(splice[b]['e1i']) + "\t" + \
                            str(splice[b]['i']) + "\t" + str(splice[b]['ie2']) + "\t" + \
                            str(splice[b]['e2']) + "\t" + str(splice[b]['e2u']) + "\t" + \
                            str(splice[b]['u']))
            b += 1
        else:
            # wave is before bin
            # print "b: %i, w: %i, wave is BEFORE, start: %s, end: %s, pos: %s, %s %s" % (b, w, splice[b]['start'], splice[b]['end'], waves[w]['pos'], splice[b]['chr'], waves[w]['chr'])
            w += 1

    while b < len(splice):
        # if ended because got to end of waves
        # need to write statistics for remaining bins
        # print "filling in remaining bins with 0s"
        print_queue.put(splice[b]['gene'] + "\t" + splice[b]['chr'] + "\t" + \
                            str(splice[b]['p1']) + "\t" + str(splice[b]['p2']) + "\t" + \
                            str(splice[b]['e11']) + "\t" + str(splice[b]['e12']) + "\t" + \
                            str(splice[b]['i1']) + "\t" + str(splice[b]['i2']) + "\t" + \
                            str(splice[b]['e21']) + "\t" + str(splice[b]['e22']) + "\t" + \
                            str(splice[b]['u1']) + "\t" + str(splice[b]['u2']) + "\t" + \
                            str(splice[b]['p']) + "\t" + str(splice[b]['pe1']) + "\t" + \
                            str(splice[b]['e1']) + "\t" + str(splice[b]['e1i']) + "\t" + \
                            str(splice[b]['i']) + "\t" + str(splice[b]['ie2']) + "\t" + \
                            str(splice[b]['e2']) + "\t" + str(splice[b]['e2u']) + "\t" + \
                            str(splice[b]['u']))
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

    # quick summary statistics
    unassigned = 0
    for i in waves:
        if not i["used"]:
            unassigned += 1


    if(heisig):
        print "Height threshold applied to waves:", thresh
    else:
        print "Sigma threshold applied to waves:", thresh

    ln = 0    # total number of genes
    ctp = 0    # count of peaks in promoters
    ctpe1 = 0    # count of peaks in promoter/exon1 region
    cte1 = 0
    cte1i = 0
    cti = 0
    ctie2 = 0
    cte2 = 0
    cte2u = 0
    ctu = 0
    emptygenes = 0

    for line in splice:
        ln += 1
        ctp += line['p']
        ctpe1 += line['pe1']
        cte1 += line['e1']
        cte1i += line['e1i']
        cti += line['i']
        ctie2 += line['ie2']
        cte2 += line['e2']
        cte2u += line['e2u']
        ctu += line['u']
        if line['p'] == 0 and line['e1'] == 0 and line['i'] == 0 and line['e2'] == 0 and line['u'] == 0:
            # no waves in this gene
            emptygenes += 1
            ln -= 1    # dont use in calculating the average

    avgp = float(ctp) / ln
    avgpe1 = float(ctpe1) / ln
    avge1 = float(cte1) / ln
    avge1i = float(cte1i) / ln
    avgi = float(cti) / ln
    avgie2 = float(ctie2) / ln
    avge2 = float(cte2) / ln
    avge2u = float(cte2u) / ln
    avgu = float(ctu) / ln
    print "%s waves were not part of a spliced gene" % unassigned
    print "%s genes had no waves" % emptygenes
    print "Region\tAverage_num_waves"
    print "Prom\t%f" % avgp
    print "Exon_1\t%f" % avge1
    print "Intron\t%f" % avgi
    print "Exon_2\t%f" % avge2
    print "3'_UTR\t%f" % avgu
    print "\n"
    print "prom_exon1\t%f" % avgpe1
    print "exon1_intron\t%f" % avge1i
    print "intron_exon2\t%f" % avgie2
    print "exon2_utr\t%f" % avge2u


if __name__ == "__main__":
    if len(sys.argv) <= 3:
        print ("This program requires the name of the spliced gene file, file of ChIP-chip waves files, and output/path")
        print" eg. python peaks_in_splicesites.py /directory/splice.csv /directory/file.waves directory/output/"
        sys.exit()
    sf = sys.argv[1]
    wfof = sys.argv[2]
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
        th = -1
    elif at == "N" or at == "n":
        at = False
        th = int(raw_input("What should the threshold be? "))
    else:
        print "invalid entry."
        sys.exit()
    fof = open(wfof, 'r')
    for wf in fof:
        find_waves_in_spliced_genes(sf, wf.rstrip(), out, at, sh, th)
    fof.close()


