'''
Use this function with Care!  It can be used to delete the data from a specific sample (file_name).  Probably requires further testing
after modifications were made, subsequent to last use.
Created on Sep 10, 2013
Modified for yeast_epigenetics Oct 23, 2013

@author: afejes, sbrown
'''
import os
import sys
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import common_utilities as cu
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters


from bson.objectid import ObjectId


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("samplename", help = "The name of the sample to be removed", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)

    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    found = mongo.find("samples", {"file_name":args.samplename}, {"_id": True}).count()
    print "found %s sample(s) to delete with file_name %s" % (found, args.samplename)
    curs = mongo.find("samples", {"file_name":args.samplename}, {"_id": True})
    samples = cu.CreateListFromOIDs(curs)
    # print "curs is:", curs
    print "ObjectIds for sample(s): ", samples
    for w in samples:
        print "found %s waves to delete from %s" % (mongo.find("waves", {"sample_id":ObjectId(w)}).count(), w)
        removed = mongo.remove("waves", {"sample_id":ObjectId(w)}, True)
        print "%s waves removed from %s" % (removed['n'], w)
    removed = mongo.remove("samples", {"file_name":args.samplename}, True)
    print "samples removed = %s" % (removed['n'])
