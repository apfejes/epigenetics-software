'''
Created on 2013-04-09

@author: jyeung
'''


import sys
import os
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)

from MongoDB.mongoUtilities import Mongo_Connector, FilesInDirectory


# database_name = 'human_epigenetics'
database_name = 'jake_test'
collection_name = 'methylation'
# directory = '/home/jyeung/Documents/Outputs/Down'


def InsertMethylData(directory):
    # Connect to database
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    collection = mongo.db[collection_name]
    # Grab all files in that directory.
    files = FilesInDirectory.Files(directory)
    Bulk = files.InsertDataToDB(collection)
    return Bulk


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Directory must be given on the command line.')
        sys.exit()
    starttime = time.time()
    directory = sys.argv[1]
    print('Grabbing beta and expression text files from %s' %directory)
    InsertMethylData(directory)
    print('Done in %i seconds' %(time.time() - starttime))