'''
Created on Oct 18, 2013

@author: sbrown

This allows sample information to be uploaded into the database, designed for yeast ChIP-chip data, although it can be tailored to other sample types.

'''

import sys
import os
import argparse


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters
import Mongo_Connector

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")

import StringUtils



def run(PARAM, metadata_file, tohide):
    '''reads metadata_file, and updates sample entries in database'''

    while not os.path.isfile(metadata_file):
        print "Unable to find file %s" % metadata_file
        sys.exit()

    print "Data being imported into database: ", PARAM.get('default_database')

    print "opening connection(s) to MongoDB..."
    mongo = Mongo_Connector.MongoConnector(PARAM.get("server"), PARAM.get("port"), PARAM.get('default_database'))

    print "processing %s..." % metadata_file

    f = open(metadata_file, 'r')
    firstrow = True
    collection_name = 'samples'
    missing = 0
    for line in f:
        sample_update = {}
        if not firstrow:
            a = line.split("\t")
            # # Find file name
            file_name = StringUtils.rreplace(a[0], ".CEL", ".normalized.waves", 1)
            print "Checking for file %s in database %s" % (file_name, PARAM.get('default_database'))
            # check if entry exists in database
            if mongo.find(collection_name, {"file_name":file_name}, {"_id":1}).count() > 0 :
                print "Entry exists; updating metadata for ", file_name
                # Update other parameters
                sample_update["exp_date"] = a[1]
                sample_update["strain_number"] = a[2]
                sample_update["strain_background"] = a[3]
                sample_update["mutations"] = a[4]
                sample_update["researcher"] = a[5]
                sample_update["type"] = a[6]
                sample_update["antibody"] = a[7]
                sample_update["catalog_number"] = a[8]
                sample_update["antibody_volume"] = a[9]
                sample_update["array_type"] = a[10]
                sample_update["array_lot_number"] = a[11]
                sample_update["protocol"] = a[12]
                sample_update["crosslinking_time"] = a[13]
                sample_update["pubmed_id"] = a[14]
                sample_update["sample_id"] = a[15]
                sample_update["comments"] = a[16]
                if a[16] == "\n":
                    sample_update["comments"] = ""
                if tohide:
                    sample_update['hide'] = True
                else:
                    sample_update['hide'] = False    # now that metadata is added, unhide sample

                # update entries
                mongo.update(collection_name, {"file_name":file_name}, {"$set": sample_update})
                print "\tFinished updating metadata for ", file_name
            else:
                print "NOT FOUND: ", file_name
                missing += 1
        else:
            firstrow = False
    print "Done all updates from metadata file ", metadata_file
    if missing > 0:
        print "%s files were unable to be updated as no matching file_name was found in the waves table." % missing
    mongo.close()





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_file", help = "meta data file to import", type = str)
    parser.add_argument("-hide", help = "if this flag is provided, then the hide flag is set to true, otherwise, it is set to false.", action = "store_true")
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    run(p, args.metadata_file, args.hide)
    print "Completed."
