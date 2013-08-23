'''
Created on 2013-04-15

@author: afejes
'''


import sys
import os
import multiprocessing
import time
import scipy.odr as odr

# from bson.objectid import ObjectId


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")

import Parameters
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector, common_utilities
import PrintThread
from Statistics import Kolmogorov_Smirnov as stats
# sys.path.insert(0, _root_dir + os.sep + "Illustration")
# import Histogram as histogram
# import ScatterPlot as scatterplot

class WavePair():
    # i, j, p, pos1, pos2, stddev1, stddev2

    def __init__(self, chromosome, i, j, p, pos1, pos2, stddev1, stddev2, height1, height2):
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

    def get_i(self):
        return self.i

    def get_j(self):
        return self.j

    def get_ht1(self):
        return self.ht1

    def get_ht2(self):
        return self.ht2

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
        return str(self.chromosome) + "\t" + str(self.pos1) + "\t" + \
            str(self.pos2) + "\t" + str(self.stddev1) + "\t" + \
            str(self.stddev2) + "\t" + str(self.ht1) + "\t" + \
            str(self.ht2) + "\t" + str(self.p)

    def type(self):
        return "Wavepair"


def run():
    # build mongo connection
    print "opening connection(s) to MongoDB..."
    db_name = "human_epigenetics"
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    util = common_utilities.MongoUtilities(mongo)    # get names of available samples

    print_queue = multiprocessing.Queue()
    # launch thread to read and process the print queue
    print_thread = PrintThread.StringWriter(print_queue, "/home/afejes/temp/", "waves.txt", True, True)

    # ask user for name of sample

    results = util.get_chip_seq_sample_names()
    s = [len(results)]
    c = 1
    for r in results:
        s.append(r)
        print ("%i. %s") % (c, r)
        c += 1
    print "here are the names of available samples: which one do you want to use as a sample?"
    user_input = raw_input("enter the number(s). If using more than one, separate by a coma:")

    samples = []
    if "," in user_input:
        t = [int(o) for o in user_input.split(",")]
        for i in t:
            samples.append(s[i])
    else:
        y = int(user_input)
        if y > s[0]:
            print "input number too big.  Quitting"
            sys.exit()
        samples.append(s[int(user_input)])
    print samples
    # ask user for name of control()

    # process s and samples.

    results = util.get_chip_seq_sample_names()
    s = [len(results)]
    c = 1
    for r in results:
        s.append(r)
        print ("%i. %s") % (c, r)
        c += 1
    print "here are the names of available samples: which one do you want to use as a control?"
    user_input = raw_input("enter the number(s). If using more than one, separate by a coma:")

    controls = []


    if "," in user_input:
        t = [int(o) for o in user_input.split(",")]
        for i in t:
            controls.append(s[i])
    else:
        y = int(user_input)
        if y > s[0]:
            print "input number too big.  Quitting"
            sys.exit()
        controls.append(s[int(user_input)])
    print controls

    chromosomes = util.get_chromosome_names()


    id_s = map(util.get_sample_id_from_name, samples)
    id_r = map(util.get_sample_id_from_name, controls)
    # print "sample ids", id_s
    # print "control ids", id_r
    x = []
    y = []
    for chromosome in chromosomes:    # for each chromosome
        print "chromosome %s" % chromosome
        waves1 = None
        waves2 = None
        for i in id_s:
            # print "i %s" % i
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, [("chr", 1)])
            waves1 = common_utilities.CreateListFromCursor(cursor)
        for i in id_r:
            # print "i %s" % i
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, [("chr", 1)])
            waves2 = common_utilities.CreateListFromCursor(cursor)
            # print "list1.length", len(list1)
            # for j in range(len(list1)):
            #    print list1[j]
        # figure out which peaks are same between the two samples.
        both = []

        i = 0
        j = 0
        max_i = len(waves1)
        max_j = len(waves2)
        while (i < max_i and j < max_j):
            chromosome = waves1[i]['chr']
            pos_i = waves1[i]['pos']
            sdv_i = waves1[i]['stddev']
            ht_i = waves1[i]['height']
            jt = j - 1
            while jt >= 0 and waves2[jt]['pos'] > (pos_i - 4 * sdv_i) :
                # print "jt - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[jt]['pos'], waves2[jt]['stddev']
                pvalue = stats.ks_test(pos_i, sdv_i, waves2[jt]['pos'], waves2[jt]['stddev'])
                if (pvalue != 0):
                    w = WavePair(chromosome, i, jt, pvalue, pos_i, waves2[jt]['pos'], sdv_i, waves2[jt]['stddev'], ht_i, waves2[jt]['height'])
                    if pvalue < 0.1:
                        print_queue.put(w.to_string())
                    both.append(w)
                jt -= 1
            while j < max_j and waves2[j]['pos'] < (pos_i + 4 * sdv_i):
                # print "j  - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[j]['pos'], waves2[j]['stddev']
                pvalue = stats.ks_test(pos_i, sdv_i, waves2[j]['pos'], waves2[j]['stddev'])
                if (pvalue != 0):
                    w = WavePair(chromosome, i, j, pvalue, pos_i, waves2[j]['pos'], sdv_i, waves2[j]['stddev'], ht_i, waves2[j]['height'])
                    if pvalue < 0.1:
                        print_queue.put(w.to_string())
                    both.append(w)
                j += 1
            i += 1
            # print "i %s and max_i %s", i, max_i


        # decide which peaks to use for normalization - make changes here.
        for b in both:
            ratio = float(b.get_ht1()) / b.get_ht2()
            if b.p < 0.0005 and ratio > (float(1) / 20) and ratio < 20:
                x.append(b.get_ht1())
                y.append(b.get_ht2())


    # h1 = histogram.Histogram("/home/afejes/temp/test_hist_x.svg", 100, x_max = 100)
    # h1.add_data(x)
    # h1.bin_data()
    # h1.build()
    # h1.save()

    # h2 = histogram.Histogram("/home/afejes/temp/test_hist_y.svg", 100, x_max = 100)
    # h2.add_data(y)
    # h2.bin_data()
    # h2.build()
    # h2.save()

    # NORMALIZATION
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
        # normalize the heights

    # bp = scatterplot.ScatterPlot("/home/afejes/temp/test_plot.svg", 1200, 600)
    # bp.add_and_zip_data(x, y)
    # bp.add_regression(coeff)
    # bp.build()
    # bp.save()

    # filter out from control
    paired_data = []
    max_i = len(waves1)
    max_j = len(waves2)
    while (i < max_i and j < max_j):
        chromosome = waves1[i]['chr']
        pos_i = waves1[i]['pos']
        sdv_i = waves1[i]['stddev']
        ht_i = waves1[i]['height']
        jt = j - 1
        none_found = True
        best = None
        while jt >= 0 and waves2[jt]['pos'] > (pos_i - 4 * sdv_i) :
            # print "jt - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[jt]['pos'], waves2[jt]['stddev']
            pvalue = stats.ks_test(pos_i, sdv_i, waves2[jt]['pos'], waves2[jt]['stddev'])
            if (pvalue != 0):
                w = WavePair(chromosome, i, jt, pvalue, pos_i, waves2[jt]['pos'], sdv_i, waves2[jt]['stddev'], ht_i, waves2[jt]['height'])
                if best is None:
                    best = w
                    none_found = False
                elif pvalue < best.pvalue:
                    best = w
                    none_found = False
            jt -= 1
        while j < max_j and waves2[j]['pos'] < (pos_i + 4 * sdv_i):
            # print "j  - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[j]['pos'], waves2[j]['stddev']
            pvalue = stats.ks_test(pos_i, sdv_i, waves2[j]['pos'], waves2[j]['stddev'])
            if (pvalue != 0):
                w = WavePair(chromosome, i, j, pvalue, pos_i, waves2[j]['pos'], sdv_i, waves2[j]['stddev'], ht_i, waves2[j]['height'])
                if best is None:
                    best = w
                    none_found = False
                elif pvalue < best.pvalue:
                    best = w
                    none_found = False
            j += 1
        if none_found:
            w = WavePair(chromosome, i, -1, -1, pos_i, -1, sdv_i, -1, ht_i, 0)
            paired_data.append(w)
        else:
            paired_data.append(best)

        i += 1

    print "The list of paried data is %i:" % (len(paired_data))
    for b in paired_data:
        if (b.get_ht1 > b.get_ht2 * coeff):
            print_queue.put(b.to_string())




        # return waves that are unique to sample
    if print_thread is None or not print_thread.is_alive():
        pass
    else:
        while print_queue.qsize() > 0:
            print "waiting on print_queue to empty", print_queue.qsize()
            time.sleep(1)
        print_thread.END_PROCESSES = True


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
    if len(sys.argv) <= 1:
        print ("This program requires the name of the database config file.")
        print" eg. python ImportWaveToDB.py /directory/database.conf"
        sys.exit()
    conf_file = sys.argv[1]
    param = Parameters.parameter(conf_file)
    run()
    print "Completed."
