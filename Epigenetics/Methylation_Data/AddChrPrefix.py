'''
Created on 2013-05-02

@author: jyeung
'''

import sys
import os
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector


database_name = 'human_epigenetics'
# database_name = 'jake_test'
arrayQuery = {'array_type': 'humanmethylation450_beadchip'}



def AddChrPrefix(collection_name, chr_list):
    starttime = time.time()
    for c in chr_list:
        chrQuery = {'chr': c}
        updateDict = {'CHR': ''.join(['chr', c])}
        setDict = {'$set': updateDict}
        print 'Adding chr prefix for CHR fields containing %s' % (c)
        mongo.update(collection_name, chrQuery, setDict)

    distinct = mongo.distinct(collection_name, 'chr')
    print 'chromosomes updated to:'
    print distinct

    print 'Done in %i seconds' % (time.time() - starttime)

if __name__ == "__main__":

    annotation_name = 'annotations'

    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    # mongo.ensure_index(annotation_name, 'chr')  # don't index just on chromosome name

    chromosome_list = [str(i) for i in range(1, 22)]    # Create an expected list of chromosomes
    chromosome_list.append('X')
    chromosome_list.append('Y')
    print 'Adding prefix chr to chromosome field in methyl450 arrays...'
    AddChrPrefix(annotation_name, chromosome_list)


