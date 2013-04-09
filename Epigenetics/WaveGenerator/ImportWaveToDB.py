'''
Created on 2013-03-27

@author: afejes
'''
from MongoDB.mongoUtilities import Mongo_Connector
import Parameters
import sys


def run(file_name, database_name, collection_name):
    '''simple script for reading in a wave file and inserting it into a table in a mongodb database.'''
    print "processing %s..." % file_name

    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    print "Before insert, collection \'%s\' contains %i records" % \
                        (collection_name, mongo.count(collection_name))
    f = open(file_name, 'r')    # open file
    for line in f:
        if line.startswith("#"):
            continue
        else:
            a = line.split("\t")
            wave = {}
            wave["chromosome"] = a[0]
            wave["position"] = a[1]
            wave["stddev"] = a[2]
            wave["item"] = a[3]
            mongo.insert("wave", wave)
    f.close()
    print "Collection \'%s\' now contains %i records" % \
                        (collection_name, mongo.count(collection_name))
    mongo.close()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print ("This program requires the name of the wave file to import and the " +
        "database config file, as well as the database name and collection name")
        print" eg. python ImportWaveToDB.py /directory/data.waves /directory/database.conf"

    file_name = sys.argv[1]
    conf_file = sys.argv[2]
    database_name = sys.argv[3]    # waves
    collection_name = sys.argv[4]    # wave
    p = Parameters.parameter(conf_file)
    run(file_name, database_name, collection_name)
    print "Completed."

