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
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector


database_name = 'human_epigenetics'
collection_name = 'methylation'
# directory = '/home/jyeung/Documents/Outputs/Down'

def InsertDataToDB(collection, data):
    # fdata is a dictionary which is organized as:
    # data{probe_id:(sample_id, beta, mvalue)}
    # data = {'c001':(sampA, 0,0), 'c002':(sampB,1,2), 'c003':(sampC,4,5)}
    BulkInsert = []
    count = 0
    number_of_inserts = 0
    t0 = time.time()

    for probe_id, (sample_id, beta, mvalue) in data.iteritems():
        document = {}
        document['sample_id'] = sample_id
        document['probe_id'] = probe_id
        document['beta_value'] = float(beta)
        document['m_value'] = float(mvalue)
        BulkInsert.append(document)

        if count % 100 == 0:
            number_of_inserts += len(BulkInsert)
            collection.insert(BulkInsert)
            print(('{0}{1:,}{2}{3}{4}').format('    ', len(BulkInsert), 'documents inserted in', (time.time() - t0), ' seconds.'))
            print(('{0}{1:,}').format('The number of added documents adds up to', number_of_inserts))
            t0 = time.time()
            BulkInsert = []

    return number_of_inserts

def InsertMethylData(db_name, coll_name, data):
    starttime = time.time()

    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    collection = mongo.db[coll_name]
    totalfiles = InsertDataToDB(collection, data)

    print('*** A total of %i documents were addded to the collection. ***' % totalfiles)
    print('\nDone in %i seconds' % (time.time() - starttime))
    print('{0}{1}{2}'.format('*** There are now ',
                         str(collection.count()),
                             ' docs in the collection. ***'))
    t0 = time.time()
    print("Updating indexes in background...")
    mongo.ensure_index(collection, 'probe_id', {'background':True})
    print('\nDone in %i seconds' % (time.time() - t0))

    return None
