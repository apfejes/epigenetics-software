'''
Created on Oct 18, 2013

@author: sbrown
'''

import sys
import os


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Parameters
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



def run(PARAM, metadata_file, db_name):
    '''reads metadata_file, and updates sample entries in database'''
    
    while not os.path.isfile(metadata_file):
        print "Unable to find file %s" % metadata_file
        sys.exit()
    
    print "Data being imported into database: ", db_name
    
    print "opening connection(s) to MongoDB..."
    mongo = Mongo_Connector.MongoConnector(PARAM.get_parameter("server"), PARAM.get_parameter("port"), db_name)
    
    print "processing %s..." % metadata_file
    
    f = open(metadata_file, 'r')
    firstrow = True
    collection_name = 'samples'
    for line in f:
        sample_update = {}
        if not firstrow:
            a = line.split("\t")
            ## Find file name
            file_name = StringUtils.rreplace(a[0],".CEL",".normalized.waves",1)
            print "Checking for file %s in database %s" % (file_name, db_name)
            #check if entry exists in database
            if mongo.find(collection_name, {"file_name":file_name}, {"_id":1}).count() > 0 :
                print "Entry exists; updating metadata for ", file_name
                #Update other parameters
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
                sample_update["comments"] = a[15]
                if a[15] == "\n":
                    sample_update["comments"] = ""
                #update entries
                mongo.update(collection_name, {"file_name":file_name}, {"$set": sample_update})
                print "Finished updating metadata for ", file_name
            else:
                print "NOT FOUND: ", file_name
        else:
            firstrow = False
    print "Done all updates from metadata file ", metadata_file
    mongo.close()



if __name__ == '__main__':
    if len(sys.argv) <= 3:
        print ("This program requires the name of the database config file, the name of the metadata file, and database")
        print " eg. python ImportWaveToDB.py /directory/database.conf input/metadata.tsv test"
        print " for instance, you can find a demo config file in Epigenetics/MongoDB/database.conf "
        sys.exit()
    conf_file = sys.argv[1]
    in_file = sys.argv[2]
    db = sys.argv[3]
    p = Parameters.parameter(conf_file)
    run(p, in_file, db)
    print "Completed."