'''
Use this function with Care!  It can be used to delete the data from a specific project.  Probably requires further testing
after modifications were made, subsequent to last use.
Created on Sep 10, 2013

@author: afejes
'''
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import common_utilities as cu


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Project name to delete must be given.')
        sys.exit()
    proj_name = sys.argv[1]

    db_name = "human_epigenetics"
    mongodb = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    curs = mongodb.find("samples", {"project":proj_name}, {"_id": True})
    samples = cu.CreateListFromOIDs(curs)
    removed = mongodb.remove("methylation", {"sampleid": {"$in": samples}}, True)
    print "data points removed = %s" % (removed['n'])
    removed = mongodb.remove("samples", {"project":proj_name}, True)
    print "samples removed = %s" % (removed['n'])
