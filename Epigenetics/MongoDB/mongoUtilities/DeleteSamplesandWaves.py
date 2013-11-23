'''
Use this function with Care!  It can be used to delete the data from a specific sample (file_name).  Probably requires further testing
after modifications were made, subsequent to last use.
Created on Sep 10, 2013
Modified for yeast_epigenetics Oct 23, 2013

@author: afejes, sbrown
'''
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import common_utilities as cu

from bson.objectid import ObjectId


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Sample name to delete must be given (file_name.normalized.waves).')
        sys.exit()
    proj_name = sys.argv[1]

    db_name = "yeast_epigenetics"
    mongodb = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    found = mongodb.find("samples", {"file_name":proj_name}, {"_id": True}).count()
    print "found %s sample(s) to delete with file_name %s" % (found, proj_name)
    curs = mongodb.find("samples", {"file_name":proj_name}, {"_id": True})
    samples = cu.CreateListFromOIDs(curs)
    # print "curs is:", curs
    print "ObjectIds for sample(s): ", samples
    for w in samples:
        print "found %s waves to delete from %s" % (mongodb.find("waves", {"sample_id":ObjectId(w)}).count(), w)
        removed = mongodb.remove("waves", {"sample_id":ObjectId(w)}, True)
        print "%s waves removed from %s" % (removed['n'], w)
    removed = mongodb.remove("samples", {"file_name":proj_name}, True)
    print "samples removed = %s" % (removed['n'])
