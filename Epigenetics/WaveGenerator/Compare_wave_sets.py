'''
Created on 2013-04-15

@author: afejes
'''


import sys
import os
# from bson.objectid import ObjectId


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")
import Parameters
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector, common_utilities
from WaveGenerator.Utilities.Statistics import MyClass as stats

class WavePair():
    # i, j, p, pos1, pos2, stddev1, stddev2

    def __init__(self, i, j, p, pos1, pos2, stddev1, stddev2):
        self.i = i
        self.j = j
        self.p = p
        self.pos1 = pos1
        self.pos2 = pos2
        self.stddev1 = stddev1
        self.stddev2 = stddev2

    def get_i(self):
        return self.i

    def get_j(self):
        return self.j

    def to_string(self):
        return str(self.pos1) + " " + str(self.pos2) + " " + str(self.stddev1) + " " + str(self.stddev2)

    def type(self):
        return "Wavepair"


def run():
    # build mongo connection
    print "opening connection(s) to MongoDB..."
    db_name = "human_epigenetics"
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    util = common_utilities.MongoUtilities(mongo)    # get names of available samples

    # ask user for name of sample

    results = util.get_chip_seq_sample_names()
    s = [len(results)]
    c = 1
    for r in results:
        s.append(r)
        print ("%i. %s") % (c, r)
        c += 1
    print "here are the names of available samples: which one do you want to use?"
    user_input = raw_input("enter the number(s). If using more than one, separate by a coma:")

    samples = []
    if "," in user_input:
        t = map(int, user_input.split(","))
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
    print "here are the names of available samples: which one do you want to use?"
    user_input = raw_input("enter the number(s). If using more than one, separate by a coma:")

    controls = []
    if "," in user_input:
        t = map(int, user_input.split(","))
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
    print "sample ids", id_s
    print "control ids", id_r
    for chromosome in chromosomes:    # for each chromosome
        print "chromosome %s" % chromosome
        waves1 = None
        waves2 = None
        for i in id_s:
            print "i %s" % i
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, "pos")
            waves1 = CreateListFromCursor(cursor)
        for i in id_r:
            print "i %s" % i
            cursor = mongo.find("waves", {"sample_id": i[0], "chr": chromosome}, None, "pos")
            waves2 = CreateListFromCursor(cursor)
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
            pos_i = waves1[i]['pos']
            sdv_i = waves1[i]['stddev']
            jt = j
            while jt >= 0 and waves2[jt]['pos'] > (pos_i - 4 * sdv_i) :
                print "jt - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[jt]['pos'], waves2[jt]['stddev']
                p = stats.ks_test(pos_i, sdv_i, waves2[jt]['pos'], waves2[jt]['stddev'])
                if (p[0] != 0 and p[1] != 0):
                    both.append(WavePair(i, jt, p, pos_i, waves2[jt]['pos'], sdv_i, waves2[jt]['stddev']))
                jt -= 1
            while j < max_j and waves2[j]['pos'] < (pos_i + 4 * sdv_i):
                print "j  - waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[j]['pos'], waves2[j]['stddev']
                p = stats.ks_test(pos_i, sdv_i, waves2[j]['pos'], waves2[j]['stddev'])
                if (p[0] != 0 and p[1] != 0):
                    both.append(WavePair(i, j, p, pos_i, waves2[j]['pos'], sdv_i, waves2[j]['stddev']))
                j += 1
            i += 1
            print "i %s and max_i %s", i, max_i


        # for i in range(len(waves1)):
            # for j in range(len(waves2)):
#
                # p = stats.ks_test(waves1[i]['pos'], waves1[i]['stddev'], waves2[j]['pos'], waves2[j]['stddev'])
                # if (p[0] != 0 and p[1] != 0):
                    # print "p = ", p
                    # print "waves1[i]", waves1[i]['pos'], waves1[i]['stddev'], waves2[j]['pos'], waves2[j]['stddev']
                    # both.append(WavePair(i, j, p, waves1[i]['pos'], waves2[j]['pos'], waves1[i]['stddev'], waves2[j]['stddev']))
        for i in range(len(both)):
            print "found at %s" % both[i].to_string()



        # get the waves for that chromosome
        # normalize the heights
        # filter out from control
        # return waves that are unique to sample


def CreateListFromCursor(cursor):
    list = []
    for record in cursor:
        list.append(record)
    return list



if __name__ == '__main__':
    if len(sys.argv) < 1:
        print ("This program requires the name of the database config file.")
        print" eg. python ImportWaveToDB.py /directory/database.conf"

    conf_file = sys.argv[1]
    p = Parameters.parameter(conf_file)
    run()
    print "Completed."
