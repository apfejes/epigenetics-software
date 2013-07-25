'''
Created on 2013-07-25

@author: sperez
'''


import sys
import os
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector, FilesInDirectory


database = 'human_epigenetics'



def InsertBatchToDB(self, collection, annotationdata):
    starttime = time.time()

    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database)
    collection = mongo.db["annotations"]

    BulkInsert = []
    count = 0
    number_of_inserts = 0
    t0 = time()

    for probe_dict in annotationdata:    # for each row in array of annotations
        BulkInsert.append(probe_dict)

        if len(BulkInsert) % 1000 == 0:
            number_of_inserts += len(BulkInsert)
            collection.insert(BulkInsert)
            print "%i annotation documents inserted in %i seconds." % (len(BulkInsert), time() - t0)
            print "The number of added documents adds up to %s" % (number_of_inserts)
            t0 = time()
            BulkInsert = []

    number_of_inserts += len(BulkInsert)
    collection.insert(BulkInsert)

    print "*** A total of %i documents were addded to the annotation collection. ***" % (totalfiles)
    print "\nDone in %i seconds" % (time.time() - starttime)
    print "*** There are now %i docs in the annotation collection. *** " % (collection.count())
    t0 = time.time()
    print "Updating indexes in background..."
    mongo.ensure_index(collection, 'mapinfo', {'background':True})
    print '\nDone in %i seconds' % (time.time() - t0)

    return None

