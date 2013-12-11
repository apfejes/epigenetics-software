'''
Created on 2013-12-09
- This script will find peaks that are unique to the chosen sample.
- First it pairs peaks, and using paired peaks, normalizes peak heights.
- It then uses unique peaks in the control to determine the character of the noise.
- Using this information, it removes noise from the unique sample peaks, and returns the unique peaks.
@author: sbrown
'''


import sys
import os
import multiprocessing
import time
import scipy.odr as odr
from scipy import stats as scipystats
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
from Statistics import Kolmogorov_Smirnov as stats
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

    DEBUG_PRINT = True

    # build mongo connection
    print "opening connection(s) to MongoDB..."
    util = common_utilities.MongoUtilities(mongo)    # get names of available samples


    # ask user for name of sample
    results = util.get_chip_sample_names()
    s = [len(results)]
    c = 1
    print "Here are the names of available samples:"
    for r in results:
        s.append(r)
        print ("%i. %s") % (c, r)
        c += 1

    # SAMPLE SELECTION
    user_input = raw_input("Which one would you like to use as the sample? ")
    samples = []
    t = int(user_input)
    if t > c:
        print "your input number is too big. Quitting"
        sys.exit()
    samples.append(s[int(user_input)])
    print "you have chosen: ", samples

    print "which one do you want to use as a control?"
    user_input = raw_input("Which one would you like to use as the control? ")
    controls = []
    y = int(user_input)
    if y > c:
        print "your input number is too big. Quitting"
        sys.exit()
    controls.append(s[int(user_input)])
    print "you have chosen: ", controls

    # USER PARAMETERS
    print "\n"
    user_ks_fdr = float(raw_input("What False Discovery Rate is acceptable for pairing peaks [0.00 - 1.00]: "))

    chromosomes = util.get_chromosome_names()
    id_s = [util.get_sample_id_from_name(s, db) for s in samples]
    id_r = [util.get_sample_id_from_name(c, db) for c in controls]

    # FETCH PEAKS
    all_paired = []
    sample_unpaired = []
    control_unpaired = []
    print "Reading waves from database and finding pairs..."
    for chromosome in chromosomes:    # for each chromosome
        waves1 = []
        waves2 = []
        print "chromosome %s" % chromosome
        for i in id_s:
            # FOR EACH WAVE IN SAMPLE
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, [("pos", 1)])
            waves1 = common_utilities.CreateListFromCursor(cursor)
        for i in id_r:
            # FOR EACH WAVE IN CONTROL
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, [("pos", 1)])
            waves2 = common_utilities.CreateListFromCursor(cursor)

        # PAIR PEAKS
        i = 0
        j = 0
        max_i = len(waves1)
        max_j = len(waves2)
        print "Now pairing peaks on chromosome ", chromosome
        while (i < max_i and j < max_j):
            chromosome = waves1[i]['chr']
            pos_i = waves1[i]['pos']
            sdv_i = waves1[i]['stddev']
            ht_i = waves1[i]['height']
            jt = j - 1
            none_found = True
            best = None
            while jt >= 0 and (waves2[jt]['pos'] + 4 * waves2[jt]['stddev']) > (pos_i - 4 * sdv_i) :
                # print "jt - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[jt]['pos'], waves2[jt]['stddev']
                # stats.ks_test returns large number for similar distribution
                pvalue = stats.ks_test(pos_i, sdv_i, waves2[jt]['pos'], waves2[jt]['stddev'])
                if chromosome == "chr1" and pos_i == 951654:
                    print "sample peak %s (%s, %s) paired with %s (%s, %s) has p-value %s" % (pos_i, ht_i, sdv_i, waves2[jt]['pos'], waves2[jt]['height'], waves2[jt]['stddev'], pvalue)
                if (pvalue != 1.0):
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
                if chromosome == "chr1" and pos_i == 951654:
                    print "sample peak %s (%s, %s) paired with %s (%s, %s) has p-value %s" % (pos_i, ht_i, sdv_i, waves2[j]['pos'], waves2[j]['height'], waves2[j]['stddev'], pvalue)
                if (pvalue != 1.0):
                    w = WavePair(chromosome, i, j, pvalue, pos_i, waves2[j]['pos'], sdv_i, waves2[j]['stddev'], ht_i, waves2[j]['height'])
                    if best is None:
                        best = w
                        none_found = False
                    elif pvalue < best.p:
                        best = w
                        none_found = False
                j += 1

            if none_found:
                w = WavePair(chromosome, i, -1, -1, pos_i, -1, sdv_i, -1, ht_i, 0)
                sample_unpaired.append(w)
            else:
                all_paired.append(best)
            i += 1

        # FIND UNIQUE PEAKS IN CONTROL
        print "Now finding unique peaks in control on chromosome ", chromosome
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
                if (pvalue != 1.0):
                    none_found = False
                it -= 1
            while i < max_i and (waves1[i]['pos'] - 4 * waves1[i]['stddev']) < (pos_j + 4 * sdv_j):
                # print "checking %s, %s" % (i, j)
                pvalue = stats.ks_test(pos_j, sdv_j, waves1[i]['pos'], waves1[i]['stddev'])
                if (pvalue != 1.0):
                    none_found = False
                i += 1

            # print "DEBUG: wavepair is: ", w.to_string()
            if none_found:
                w = WavePair(chromosome, -1, j, -1, -1, pos_j, -1, sdv_j, 0, ht_j)
                control_unpaired.append(w)
            j += 1


    # Now determine FDR for every peak that has a pair, carry on with pairs that meet user cutoff.
    # user_ks_fdr = 0.05
    print "\nNow determining closest possible FDR to ", user_ks_fdr
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
    print "Calculating line going through KS_test p-value histogram:"
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

    # update ks_FDR value for all peaks
    for ap in all_paired:
        ap.set_k(fdr[ap.b])    # set the ks_fdr to the FDR value for that bin
        # unpair non-significant pairings
        if ap.k > user_ks_fdr:
            sw = WavePair(ap.chromosome, ap.i, -1, -1, ap.pos1, -1, ap.stddev1, -1, ap.ht1, 0)
            sample_unpaired.append(sw)
            cw = WavePair(ap.chromosome, -1, ap.j, -1, -1, ap.pos2, -1, ap.stddev2, 0, ap.ht2)
            control_unpaired.append(cw)

    print "KS-means p-value threshold is: %s and FDR is: %s" % (thresh[ans], fdr[ans])
    print "number of peaks that meet this threshold: ", numpeaks
    print "this is %s%% of the total number of peaks (pairs) analyzed (%s)" % (float(numpeaks) / len(all_paired) * 100, len(all_paired))
    print "requested FDR was: ", user_ks_fdr

    # CALCULATE NORMALIZATION ON WAVE PAIRS THAT MEET FDR
    print "Collecting wave pairs that meet FDR cutoff."
    x = []
    y = []
    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, "paired_norm_waves.txt", True, True)
    for pairs in all_paired:
        if pairs.k <= user_ks_fdr:
            # ratio = float(pairs.ht1) / pairs.ht2
            # if ratio > (float(1) / 20) and ratio < 20:
            if True:
                x.append(pairs.ht1)
                y.append(pairs.ht2)
                if DEBUG_PRINT:
                    print_queue.put("%s\t%s\t%s\t%s\t%s" % (pairs.chromosome, pairs.pos1, pairs.pos2, pairs.ht1, pairs.ht2))
    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()
    # NORMALIZATION
    print "\nCalculating normalization required for peaks."
    linear = odr.Model(f)
    mydata = odr.Data(x, y)
    myodr = odr.ODR(mydata, linear, [1])
    myodr.set_job(fit_type = 2)    # do a linear model, then use that to figure out the non-linear model - initial first guess.

    # myodr.set_iprint(final = 2)
    fit = myodr.run()
    coeff = fit.beta[::-1]
    err = fit.sd_beta[::-1]
    print "linear - least squares : coeff %s err %s" % (coeff, err)
    myodr = odr.ODR(mydata, linear, coeff)
    myodr.set_job(fit_type = 0)

    fit2 = myodr.run()
    # fit.pprint()
    if fit2.stopreason[0] == 'Iteration limit reached':
        print '(WWW) poly_lsq: Iteration limit reached, result not reliable!'
    coeff = fit2.beta[::-1]
    err = fit2.sd_beta[::-1]
    print "ODR - explicit fit: coeff %s err %s" % (coeff, err)

    # when normalizing, transform control (control height / coeff)
    # ht2 = coeff*ht1
    # TODO: in future, may want to make this fancier.
    print "Unique control peaks will be scaled by a factor of %s\n" % round(1.0 / coeff, 2)
    for i in control_unpaired:
        i.ht2 = round(float(i.ht2) / float(coeff), 2)

    # PRINT UNNORMALIZED PAIRED DATA
    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, "paired_waves.txt", True, True)

    for i in all_paired:
        print_queue.put("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (i.chromosome, i.pos1, i.pos2, i.ht1, i.ht2, i.stddev1, i.stddev2, i.p))

    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()

    if DEBUG_PRINT:
        # PRINT SAMPLE SPECIFIC PEAKS
        print_queue = multiprocessing.Queue()
        # launch thread to read and process the print queue
        print_thread = PrintThread.StringWriter(print_queue, output, "sample_waves.txt", True, True)

        for i in sample_unpaired:
            print_queue.put("%s\t%s\t%s\t%s" % (i.chromosome, i.pos1, i.ht1, i.stddev1))

        if print_thread is None or not print_thread.is_alive():
            pass
        else:
            while print_queue.qsize() > 0:
                print "waiting on print_queue to empty", print_queue.qsize()
                time.sleep(1)
            print_thread.END_PROCESSES = True
            print_thread.f.close()

        # PRINT CONTROL SPECIFIC PEAKS
        print_queue = multiprocessing.Queue()
        # launch thread to read and process the print queue
        print_thread = PrintThread.StringWriter(print_queue, output, "control_waves.txt", True, True)

        for i in control_unpaired:
            print_queue.put("%s\t%s\t%s\t%s" % (i.chromosome, i.pos2, i.ht2, i.stddev2))

        if print_thread is None or not print_thread.is_alive():
            pass
        else:
            while print_queue.qsize() > 0:
                print "waiting on print_queue to empty", print_queue.qsize()
                time.sleep(1)
            print_thread.END_PROCESSES = True
            print_thread.f.close()

    # Remove noise (sigma or height?)
    # TODO: figure this out.
    # TODO: PRINT UNIQUE PEAKS IN SAMPLE
    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, output, "unique_sample_waves.txt", True, True)

    for i in sample_unpaired:
        if i.ht1 > 20:
            print_queue.put("%s\t%s\t%s\t%s" % (i.chromosome, i.pos1, i.ht1, i.stddev1))

    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True
        print_thread.f.close()

    print "Done."


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
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    run(mongo, args.output_path, p.get('default_database'))
    print "Completed."
