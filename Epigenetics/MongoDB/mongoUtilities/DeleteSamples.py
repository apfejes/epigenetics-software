'''
Use this function with Care!  It can be used to delete the data from a specific sample (file_name).  Probably requires further testing
after modifications were made, subsequent to last use.
Created on Sep 10, 2013

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


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Sample name to delete must be given (.normalized.waves), as well as database.')
        sys.exit()
    proj_name = sys.argv[1]
    db_name = sys.argv[2]

    mongodb = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    found = mongodb.find("samples", {"file_name":proj_name}, {"_id": True}).count()
    print "found %s samples to delete", found
    curs = mongodb.find("samples", {"file_name":proj_name}, {"_id": True})
    samples = cu.CreateListFromOIDs(curs)
    print "found %s samples to delete", mongodb.find("waves", {"sample_id":{"$in":samples}}).count()
    # removed = mongodb.remove("waves", {"sample_id": {"$in": samples}}, True)
    # print "waves removed = %s" % (removed['n'])
    # removed = mongodb.remove("samples", {"file_name":proj_name}, True)
    # print "samples removed = %s" % (removed['n'])
