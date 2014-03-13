'''
Custom query to work out the variation for a specific probe.  
Created on Sep 10, 2013

@author: afejes
'''
import os
import sys
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(os.path.dirname(_cur_dir))
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import common_utilities as cu
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("probe", help = "The name of the probe", type = str)
    parser.add_argument("project", help = "The name of the project", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()

    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)

    path = "/home/afejes/temp/"
    file_name = path + args.probe + ".records"
    f = open(file_name, 'w')

    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    # ignore FASD probes.
    print "Ignoring project %s" % (args.project)
    print "Finding samples to ignore..."
    curs = mongo.find("samples", {"project":{"$ne": args.project}, "tissuetype":"buccal"}, {"_id": True})
    print "Creating list from Cursor..."
    samples_to_use = cu.CreateListFromOIDs(curs)
    print "found %s samples" % len(samples_to_use)
    # print "sample to use: %s" % samples_to_use
    print "Finding Probes..."
    curs = mongo.find("methylation", {"sid": {"$in":samples_to_use}, "pid": args.probe}, {"_id":False, "b":True})
    print "open file for output: %s" % (file_name)
    i = 0
    for record in curs:
        i += 1
        f.write("%s\n" % record['b'])
        # print "%s" % record['beta']
    print "%i values found and written to file.  File closing..." % i
    f.close()
    mongo.close()
#    removed = mongodb.remove("methylation", {"sampleid": {"$in": samples}}, True)
    # print "data points removed = %s" % (removed['n'])
#    removed = mongodb.remove("samples", {"project":proj_name}, True)
    # print "samples removed = %s" % (removed['n'])
