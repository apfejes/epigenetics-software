'''
Created on 2013-04-15

@author: afejes, sbrown

This will allow two samples to be pulled from the database, and have the waves compared. Ideally, after providing threshold values,
it will return waves which are found in both sample, waves enriched in sample, and waves enriched in control. 
Work needed to fine tune.

'''

import sys
import os
import multiprocessing
import time
# import scipy.odr as odr
from scipy import stats as scipystats
import math
import argparse

# from bson.objectid import ObjectId


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")

sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector, common_utilities
import PrintThread
from CommonUtils.Statistics import Kolmogorov_Smirnov as stats
# sys.path.insert(0, _root_dir + os.sep + "Illustration")
# import Histogram as histogram
# import ScatterPlot as scatterplot

class WavePair():
    '''An object for holding a pair of waves simultaneously'''
    # i, j, p, pos1, pos2, stddev1, stddev2

    def __init__(self, chromosome, i, j, p, pos1, pos2, stddev1, stddev2, height1, height2, ks_fdr = -1, bin_num = -1, fold_change = ""):
        '''set initial values of the two waves'''
        self.chromosome = chromosome
        self.i = i
        self.j = j
        self.p = p
        self.pos1 = pos1
        self.pos2 = pos2
        self.stddev1 = stddev1
        self.stddev2 = stddev2
        self.ht1 = height1
        self.ht2 = height2
        self.k = ks_fdr
        self.b = bin_num
        self.fc = fold_change

    def get_ratio_max(self):
        '''use this for calculating the ratio of the two peaks.
        If the second peak is smaller, it's returned as a negative number'''

        if (self.ht1 == self.ht2):
            return 1
        elif (self.ht1 > self.ht2):
            return float(self.ht1) / self.ht2
        else:
            return 0 - float(self.ht2) / self.ht1


    def to_string(self):
        '''convert a wave pair to a string for printing.'''
        return str(self.chromosome) + "\t" + str(self.pos1) + "\t" + \
            str(self.pos2) + "\t" + str(self.stddev1) + "\t" + \
            str(self.stddev2) + "\t" + str(self.ht1) + "\t" + \
            str(self.ht2) + "\t" + str(self.p) + "\t" + \
            str(self.k) + "\t" + str(self.fc)

    def set_k(self, value):
        '''update ks_fdr value for pair'''
        self.k = value

    def set_b(self, value):
        '''update bin number for pair'''
        self.b = value

    def set_fc(self, value):
        '''update fold change for pair'''
        self.fc = value

    @staticmethod
    def type():
        '''return Wavepair when asked'''
        return "Wavepair"


def run(mongo, output, db):
    '''Main module to run the compare'''
    # build mongo connection
    print "opening connection(s) to MongoDB..."
    util = common_utilities.MongoUtilities(mongo)    # get names of available samples

    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, "waves_comparison_allwaves.txt", True, True)

    # ask user for name of sample

    results = util.get_chip_sample_names()
    s = [len(results)]
    c = 1
    for r in results:
        s.append(r)
        print ("%i. %s") % (c, r)
        c += 1
    # SAMPLE SELECTION
    print "here are the names of available samples: which one do you want to use as a sample?"

    user_input = raw_input("enter the number(s). If using more than one, separate by a comma: ")
    samples = []
    if "," in user_input:
        t = [int(o) for o in user_input.split(",")]
        for y in t:
            if y > c:
                print "at least one of your input numbers is too big. Quitting"
                sys.exit()
        for i in t:
            samples.append(s[i])
    else:
        t = int(user_input)
        if t > c:
            print "your input number is too big. Quitting"
            sys.exit()
        samples.append(s[int(user_input)])
    print samples

    print "which one do you want to use as a control?"
    user_input = raw_input("enter the number(s). If using more than one, separate by a comma: ")
    controls = []
    if "," in user_input:
        t = [int(q) for q in user_input.split(",")]
        for y in t:
            if y > c:
                print "one of your input numbers is too big. Quitting"
                sys.exit()
        for i in t:
            controls.append(s[i])
    else:
        y = int(user_input)
        if y > c:
            print "your input number is too big. Quitting"
            sys.exit()
        controls.append(s[int(user_input)])
    print controls

    # USER PARAMETERS
    print "\n"
    user_ks_fdr = float(raw_input("What False Discovery Rate is acceptable for pairing peaks: "))
    print "\n"
    user_fc = float(raw_input("What minimum fold change in peak heights are you interested in: "))

    remove_noise = raw_input("\nWould you like the program to remove background noise from each sample? [y/n]: ")
    if remove_noise.lower() == "y":
        remove_noise = True
        hw = raw_input("\nShould the background noise be based on peak height or peak width? [h/w]: ")
        if hw.lower() == "h":
            hw = True
        elif hw.lower() == "w":
            hw = False
        else:
            print "invalid entry"
            sys.exit()
    elif remove_noise.lower() == "n":
        remove_noise = False
    else:
        print "invalid entry"
        sys.exit()

    two_way = raw_input("\nWould you like to perform a 2-way analysis (find unique peaks in the control sample? [y/n]: ")
    if two_way.lower() == "y":
        two_way = True
    elif two_way.lower() == "n":
        two_way = False
    else:
        print "invalid entry"
        sys.exit()

    chromosomes = util.get_chromosome_names()

    id_s = [util.get_sample_id_from_name(s, db) for s in samples]
    id_r = [util.get_sample_id_from_name(c, db) for c in controls]

    # GO THROUGH EACH CHROMOSOME AND REMOVE NOISE, PAIR PEAKS
    # Collect all wavepairs that have a pair
    # Remove background peaks for each chromosome
    all_paired = []
    all_unpaired = []
    for chromosome in chromosomes:    # for each chromosome
        print "chromosome %s" % chromosome
        waves1 = None
        waves2 = None
        for i in id_s:
            # print "i %s" % i
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, [("pos", 1)])
            waves1 = common_utilities.CreateListFromCursor(cursor)
            # print waves1
        for i in id_r:
            # print "i %s" % i
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, [("pos", 1)])
            waves2 = common_utilities.CreateListFromCursor(cursor)


        if remove_noise and hw:    # based on height
            maxheight = -1
            minheight = 999999
            for i in (waves1 + waves2):
                if i['height'] > maxheight:
                    maxheight = i['height']
                if i['height'] < minheight:
                    minheight = i['height']

            print "\nNow determining background levels for height of peaks on chromosome ", chromosome
            print "maxheight: ", maxheight
            step = round(maxheight / 100.0, 2)
            # print "step: ", step
            bins = int(maxheight / step) + 1
            if step == 0 or maxheight == -1:    # if no information for this chromosome
                pass
            else:
                counts = [0] * bins
                thresh = [0] * bins
                for i in range(0, bins):
                    thresh[i] = (i + 1) * step
                for i in (waves1 + waves2):
                    # combine h1 and h2 to determine background levels
                    # print "height:", i['height']
                    # print "step: ", step
                    # print "ind:", int(i['height'] / step)
                    counts[int(i['height'] / step)] += 1
                # print "counts are: ", counts
                x = []
                y = []
                # for i in range(10, 15):    # (0 to 9 correspond to heights 0 to 0.9, do not have)
                for i in range(int(minheight / step), int(minheight / step + 5)):
                    x.append(thresh[i])
                    y.append(counts[i])
                print "x is ", x
                print "y is ", y
                slr = scipystats.linregress(x, y)
                slope = slr[0]
                intercept = slr[1]
                print "slope: %s and intercept: %s for background peak height" % (slope, intercept)
                # find x-intercept, threshold for noise-signal
                xint = abs(intercept / slope)
                print "height threshold between noise and signal is ", xint
                # REMOVE background peaks
                waves1[:] = [x for x in waves1 if x['height'] > xint]
                waves2[:] = [x for x in waves2 if x['height'] > xint]

        if remove_noise and not hw:    # based on width
            print "Now determining background levels for width of peaks on chromosome", chromosome
            bins = 300    # based on max sigma of 300
            counts = [0] * bins
            threshes = [0] * bins
            for i in range(0, bins):
                threshes[i] = (i + 1)
            for i in (waves1 + waves2):
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
            if slope != 0:    # mitochondrial data may not exist
                xint = abs(intercept / slope)
            else:
                xint = 0
            thresh = round(xint, 2)
            print "sigma threshold between noise and signal is ", thresh
            waves1[:] = [x for x in waves1 if x['stddev'] > thresh]
            waves2[:] = [x for x in waves2 if x['stddev'] > thresh]


        # FIND PAIRS
        paired_data = []
        i = 0
        j = 0
        max_i = len(waves1)
        max_j = len(waves2)
        while (i < max_i and j < max_j):
            chromosome = waves1[i]['chr']
            # print "DEBUG: Round 2 chromosome: ", chromosome
            # print "DEBUG: waves1[i]: ", waves1[i]
            pos_i = waves1[i]['pos']
            sdv_i = waves1[i]['stddev']
            ht_i = waves1[i]['height']
            jt = j - 1
            none_found = True
            best = None
            while jt >= 0 and (waves2[jt]['pos'] + 4 * waves2[jt]['stddev']) > (pos_i - 4 * sdv_i) :
                # print "jt - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[jt]['pos'], waves2[jt]['stddev']
                pvalue = stats.ks_test(pos_i, sdv_i, waves2[jt]['pos'], waves2[jt]['stddev'])
                if (pvalue != 0):
                    w = WavePair(chromosome, i, jt, pvalue, pos_i, waves2[jt]['pos'], sdv_i, waves2[jt]['stddev'], ht_i, waves2[jt]['height'])
                    if best is None:
                        best = w
                        none_found = False
                    elif pvalue < best.p:
                        best = w
                        none_found = False
                jt -= 1
            while j < max_j and (waves2[j]['pos'] - 4 * waves2[j]['stddev']) < (pos_i + 4 * sdv_i):
                # print "j  - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[j]['pos'], waves2[j]['stddev']
                pvalue = stats.ks_test(pos_i, sdv_i, waves2[j]['pos'], waves2[j]['stddev'])
                if (pvalue != 0):
                    w = WavePair(chromosome, i, j, pvalue, pos_i, waves2[j]['pos'], sdv_i, waves2[j]['stddev'], ht_i, waves2[j]['height'])
                    if best is None:
                        best = w
                        none_found = False
                    elif pvalue < best.p:
                        best = w
                        none_found = False
                j += 1

            # print "DEBUG: wavepair is: ", w.to_string()
            if none_found:
                w = WavePair(chromosome, i, -1, -1, pos_i, -1, sdv_i, -1, ht_i, 0)
                paired_data.append(w)
                all_unpaired.append(w)
            else:
                paired_data.append(best)
                all_paired.append(best)

            i += 1

        # FIND UNIQUE PEAKS IN CONTROL
        if two_way:
            # Now find unique peaks in waves2
            # find pairs
            i = 0
            j = 0
            while (i < max_i and j < max_j):
                chromosome = waves1[i]['chr']
                # print "DEBUG: checking waves2"
                # print "DEBUG: waves1[i]: ", waves1[i]
                pos_j = waves2[j]['pos']
                sdv_j = waves2[j]['stddev']
                ht_j = waves2[j]['height']
                it = i - 1
                none_found = True
                best = None
                while it >= 0 and (waves1[it]['pos'] + 4 * waves1[it]['stddev']) > (pos_j - 4 * sdv_j) :
                    # print "checking %s, %s" % (it, j)
                    pvalue = stats.ks_test(pos_j, sdv_j, waves1[it]['pos'], waves1[it]['stddev'])
                    if (pvalue != 0):
                        none_found = False
                    it -= 1
                while i < max_i and (waves1[i]['pos'] - 4 * waves1[i]['stddev']) < (pos_j + 4 * sdv_j):
                    # print "checking %s, %s" % (i, j)
                    pvalue = stats.ks_test(pos_j, sdv_j, waves1[i]['pos'], waves1[i]['stddev'])
                    if (pvalue != 0):
                        none_found = False
                    i += 1

                # print "DEBUG: wavepair is: ", w.to_string()
                if none_found:
                    w = WavePair(chromosome, -1, j, -1, -1, pos_j, -1, sdv_j, 0, ht_j)
                    paired_data.append(w)
                    all_unpaired.append(w)

                j += 1



    # Now determine FDR for every peak that has a pair, carry on with pairs that meet user cutoff.
    # user_ks_fdr = 0.05    # TODO: input by user
    print "\nNow determining FDR threshold to use"
    bins = int(len(all_paired) * 0.05)    # bin size is 5% of total number of bins
    print "number of bins: ", bins
    counts = [0] * bins    # holds number of pairs in each bin
    thresh = [0] * bins    # holds exclusive upperbound of bin
    fdr = [1] * bins    # holds FDR for pairs in that bin
    for i in range(0, bins):
        thresh[i] = (i + 1) * 1.0 / bins    # since possible pvalue threshold from 0 to 1.
        # print "thresh[%i]: %f" % (i, thresh[i])
    for i in all_paired:
        counts[int(i.p / (1.0 / bins))] += 1    # increment count where index is p-value/sizeOfBins
        i.set_b(int(i.p / (1.0 / bins)))    # set bin number for pair
    # print "counts: ", counts

    # have counts, now find line for noise ignoring first and last bin
    bot = 1
    top = bins - 1
    print "bot: %i, top: %i" % (bot, top)
    x = []
    y = []
    # print "counts used for line: "
    for i in range(bot, top):
        x.append(thresh[i])
        y.append(counts[i])
        # print thresh[i], counts[i]
    slr = scipystats.linregress(x, y)
    slope = slr[0]
    intercept = slr[1]
    print "slope: %s and intercept: %s" % (slope, intercept)
    ans = -1    # bin that has FDR <= user FDR
    found_thresh = False
    numpeaks = 0    # number of peaks that meet that FDR
    # calculate FDR for each bin
    print "Calculating FDR for each pairing. This may take some time..."
    false = 0    # number of expected noise peaks
    total = 0    # total number of peaks encountered
    for i in range(0, bins):
        false += intercept    # add expected number of noise in each bin
        total += counts[i]    # add number of peaks seen
        fdr[i] = false / total
        # print "FDR for bin %s is %s" % (i, fdr[i])

        # check if exceeded user defined FDR
        if not found_thresh and fdr[i] > user_ks_fdr:
            ans = i - 1
            numpeaks = total - counts[i]
            found_thresh = True
            # print "Answer is ", ans

        # update ks_FDR value for all peaks in this bin
        # sig_paired = []
        for k in all_paired:
            if k.b == i:    # if peak in this bin
                k.set_k(fdr[i])    # set the ks_fdr to this value
            # if k.k < user_ks_fdr:
            #    sig_paired.append(k)    # add pair to significant paired

    print "threshold is: %s and FDR is: %s" % (thresh[ans], fdr[ans])
    print "number of peaks that meet this threshold: ", numpeaks
    print "this is %s%% of the total number of peaks (pairs) analyzed (%s)" % (float(numpeaks) / len(all_paired) * 100, len(all_paired))
    print "requested FDR was: ", user_ks_fdr

    # print paired data:
    # for i in all_paired:
    #    print_queue.put(i.to_string())

    # determine fold change for paired peaks
    for i in all_paired:
        i.set_fc(math.log(i.ht1 / i.ht2, 2))
        # print peaks with significant enrichment/depletion
        # if(i.fc != 0):
        #    print_queue.put(i.to_string())

    # determine "fold change" for unpaired peaks
    for i in all_unpaired:
        if i.ht1 == 0:    # unique control peak
            i.set_fc(math.log(1.0 / i.ht2, 2))
        else:    # unique sample peak
            i.set_fc(math.log(i.ht1 / 1.0, 2))

    # now all entries in "all_paired" have fdr and fc, all entries in "all_unpaired" have fdr of -1, fc

    # print everything, and significant results
    alldata = all_paired + all_unpaired
    # user_fc = 1.0
    for i in alldata:
        print_queue.put(i.to_string())


    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()



    # print significant results to separate file
    print_queue2 = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread2 = PrintThread.StringWriter(print_queue2, output, "waves_comparison_significantwaves.txt", True, True)

    print "Now printing significant peaks to results file"
    for i in alldata:
        if (i.k < user_ks_fdr and i.k != -1) and abs(i.fc) > user_fc:
            # print enriched peaks
            print_queue2.put(i.to_string())
        if (i.k > user_ks_fdr or i.k == -1) and abs(i.fc) > user_fc:
            # print new peaks
            print_queue2.put(i.to_string())




        # return waves that are unique to sample
    if print_thread2 is None or not print_thread2.is_alive():
        pass
    else:
        while print_queue2.qsize() > 0:
            print "waiting on print_queue to empty", print_queue2.qsize()
            time.sleep(1)
        print_thread2.END_PROCESSES = True
        print_thread2.f.close()


def f(B, x):
    '''Linear function y = m*x + b
    derived from http://docs.scipy.org/doc/scipy-dev/reference/odr.html
    '''
    # B is a vector of the parameters.
    # x is an array of the current x values.
    # x is in the same format as the x passed to Data or RealData.
    # Return an array in the same format as y passed to Data or RealData.
    return B[0] * x

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", help = "path for output", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    param = Parameters.parameter(args.dbconfig)
    if args.dbname:
        param.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(param.get('server'), param.get('port'), param.get('default_database'))
    run(mongodb, args.output_path, param.get('default_database'))
    mongodb.close()
    print "Completed."
