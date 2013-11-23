'''
This will set use to true or false for samples identified.
Used to "hide" samples in database from online browser and other analysis.
Created on Nov 19, 2013

@author: sbrown
'''
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Sample name to update must be given, along with setting.')
        print("example: python SetSampleUsage.py sample.normalized.waves false")
        sys.exit()
    proj_name = sys.argv[1]
    setting = str(sys.argv[2])
    if setting != "true" and setting != "false":
        print("setting must be 'true' or 'false', without quotes.")
        sys.exit()


    db_name = "yeast_epigenetics"
    mongodb = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    found = mongodb.find("samples", {"file_name":proj_name}, {"_id": True}).count()
    print "found %s sample(s) matching %s to update use to %s " % (found, proj_name, setting)
    sample_update = {}
    sample_update["use"] = setting
    mongodb.update("samples", {"file_name":proj_name}, {"$set": sample_update})


