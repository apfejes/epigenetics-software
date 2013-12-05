'''
Custom query to work out the variation for a specific probe.  
Created on Sep 10, 2013

@author: afejes
'''
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(os.path.dirname(_cur_dir))
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import common_utilities as cu
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Probe name must be given.')
        sys.exit()
    probe_name = sys.argv[1]

    db_name = "human_epigenetics"
    path = "/home/afejes/temp/"
    file_name = path + probe_name + ".records"
    f = open(file_name, 'w')

    p = Parameters.parameter()
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    # ignore FASD probes.
    proj_name = "FASD"
    print "Ignoring project %s" % (proj_name)
    print "Finding samples to ignore..."
    curs = mongo.find("samples", {"project":{"$ne": proj_name}, "tissuetype":"buccal"}, {"_id": True})
    print "Creating list from Cursor..."
    samples_to_use = cu.CreateListFromOIDs(curs)
    print "found %s samples" % len(samples_to_use)
    # print "sample to use: %s" % samples_to_use
    print "Finding Probes..."
    curs = mongo.find("methylation", {"sampleid": {"$in":samples_to_use}, "probeid": probe_name}, {"_id":False, "beta":True})
    print "open file for output: %s" % (file_name)
    i = 0
    for record in curs:
        i += 1
        f.write("%s\n" % record['beta'])
        # print "%s" % record['beta']
    print "%i values found and written to file.  File closing..." % i
    f.close()
#    removed = mongodb.remove("methylation", {"sampleid": {"$in": samples}}, True)
    # print "data points removed = %s" % (removed['n'])
#    removed = mongodb.remove("samples", {"project":proj_name}, True)
    # print "samples removed = %s" % (removed['n'])
