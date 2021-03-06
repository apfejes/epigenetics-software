'''
Created on 2013-04-15

@author: afejes
'''


import sys
import os
import argparse

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = _cur_dir
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")
# sys.path.insert(0, _root_dir + os.sep + "MongoDB")
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
sys.path.insert(0, _root_dir + os.sep + "MongoDB")
_mgutl_dir = _root_dir + os.sep + "MongoDB"
print "mongo util path: %s" % _mgutl_dir
print "sys.path: %s" % sys.path
# sys.path.insert(0, _root_dir + os.sep + "MongoDB")
import CommonUtils.Parameters as Parameters
import Mongo_Connector

def run(db):
    '''function to import chip-chip metadata to mongo database'''
    meta_data_file = "/home/afejes/Chip-chip/ChIPchipMetaData_v1.csv"

    # meta_data_file = raw_input('meta data file to load: ')
    # while not os.path.isfile(meta_data_file):
    #    print "Unable to find file %s" % wave_data_file
    #    meta_data_file = raw_input('meta data file to load: ')
    f = open(meta_data_file, 'r')    # open file

    print "opening connection(s) to MongoDB..."

    collection_name = "samples"

    print "processing meta data file..."
    first_line = True
    headers = []
    for line in f:
        if (first_line):
            headers = line.split("\t")
            for h in range(len(headers)):
                headers[h] = headers[h].lower()
                if headers[h].find("\n") != -1:
                    headers[h] = headers[h].replace("\n", "")
            first_line = False
        else:
            a = line.split("\t")
            if len(a[0]) < 1:
                continue
            meta = {}
            for c in range(len(a)):
                while a[c].endswith("\n"):
                    a[c] = a[c][:-2]
                meta[headers[c]] = a[c]
            print "Meta %s" % meta
            db.insert(collection_name, meta)
    f.close()
    print "Collection \'%s\' now contains %i records" % \
                        (collection_name, db.count(collection_name))
    mongo.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    run(mongo)
    mongo.close()
    print "Completed."
