'''
Use this function with Care!  It can be used to delete the data from a specific project.  Probably requires further testing
after modifications were made, subsequent to last use.
Created on Sep 10, 2013

@author: afejes
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help = "The name of the project", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)

    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    curs = mongo.find("samples", {"project":args.project}, {"_id": True})
    samples = cu.CreateListFromOIDs(curs)
    removed = mongo.remove("methylation", {"sampleid": {"$in": samples}}, True)
    print "data points removed = %s" % (removed['n'])
    removed = mongo.remove("samples", {"project":args.project}, True)
    print "samples removed = %s" % (removed['n'])
    mongo.close()
