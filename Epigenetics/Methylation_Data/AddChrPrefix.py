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
projQuery = {'project': {'$exists': True}}


def AddChrPrefix(collection_name, chromosome_list, checkQuery):
    starttime = time.time()
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    mongo.ensure_index(collection_name, 'CHR')
    rQuery = {'CHR': True}

    for c in chromosome_list:
        chrQuery = {'CHR': c}
        andQuery = {'$and': [checkQuery, chrQuery]}
        updateDict = {'CHR': 'chr%s' % c}
        setDict = {'$set': updateDict}
        print 'Adding chr prefix for CHR fields containing %s' % (c)
        mongo.update(collection_name, andQuery, setDict)

    fQuery = {'CHR': {'$exists': True}}
    annot_cursor = mongo.find(collection_name, findQuery = fQuery, returnQuery = rQuery)
    chr_list = []
    count = 0
    for annot_doc in annot_cursor:
        chr_list.append(annot_doc['CHR'])
        count += 1
    print set(chr_list)

    print 'Done in %i seconds' % (time.time() - starttime)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'methylation and annotations collection name must be given.'
        sys.exit()
    methylation_name = sys.argv[1]
    annotation_name = sys.argv[2]
    # Create an expected list of chromosomes
    chromosome_list = [str(i) for i in range(1, 22)]
    chromosome_list.append('X')
    chromosome_list.append('Y')
    print 'Adding prefix chr to chromosome field in methyl450 arrays...'
    AddChrPrefix(annotation_name, chromosome_list, arrayQuery)
    print 'Adding prefix chr to chromosome field in methylation data...'
    AddChrPrefix(methylation_name, chromosome_list, projQuery)

