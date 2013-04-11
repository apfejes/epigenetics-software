'''
Created on 2013-03-27

@author: afejes
'''
from MongoDB.mongoUtilities import Mongo_Connector
import Parameters
import sys
import os

def create_param_obj(param_file):
    '''copy of function in The WaveGenerator - should be refactored'''
    PARAM = None
    if os.path.exists(param_file):
        PARAM = Parameters.parameter(param_file)
    else:
        print "Could not find input parameter file"
        sys.exit()
    return PARAM





def run():
    '''simple script for reading in a wave file and inserting it into a table in a mongodb database.'''

    wave_data_file = raw_input('wave file to load: ')
    cell_line = raw_input('Insert name of the cell line: ')
    wave_input_file = raw_input('parameter file used to generate waves: ')
    database_name = raw_input('database name: ')    # waves
    collection_name = raw_input('collection_name: ')    # wave

    print "opening connection to database..."
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)



    print "processing %s..." % wave_input_file
    PARAM = create_param_obj(sys.argv[1])


    print "processing %s..." % wave_data_file
    print "Before insert, collection \'%s\' contains %i records" % \
                        (collection_name, mongo.count(collection_name))



    f = open(wave_data_file, 'r')    # open file
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
    if len(sys.argv) < 5:
        print ("This program requires the name of the wave file to import and the " +
        "database config file, as well as the database name and collection name")
        print" eg. python ImportWaveToDB.py /directory/data.waves /directory/database.conf"

    conf_file = sys.argv[1]
    p = Parameters.parameter(conf_file)
    run()
    print "Completed."

