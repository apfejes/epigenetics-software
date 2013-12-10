'''
This will set hide to true or false for samples identified.
Used to "hide" samples in database from online browser and other analysis.
Created on Nov 19, 2013

@author: sbrown
'''
import os
import sys
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help = "The name of the project for which the the hide setting will be adjusted", type = str)
    parser.add_argument("-hide", help = "if this flag is provided, then the hide flag is set to true, otherwise, it is set to false.", action = "store_true")
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)

    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    found = mongo.find("samples", {"file_name":args.project}, {"_id": True}).count()
    print "found %s sample(s) matching %s to update hide to %s " % (found, args.project, args.hide)
    sample_update = {}
    sample_update["hide"] = args.hide
    mongo.update("samples", {"file_name":args.project}, {"$set": sample_update})
    mongo.close()


