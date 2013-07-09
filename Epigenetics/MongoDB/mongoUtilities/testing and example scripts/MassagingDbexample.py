'''
Created on 2013-06-28

@author: sperez

Edits large amounts of data in database

'''

from time import time
import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector, MongoCurious
import MongoQuery


m = MongoCurious.MongoCurious(database = "human_epigenetics")

sample_query = m.query(collection = "samples", project = 'gecko')
print sample_query
docs = m.finddocs()
print docs

sample_labels_list = [str(doc['sample_label']) for doc in docs]
print len(sample_labels_list), 'samples to update'
print sample_labels_list

t0 = time()
mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, 'human_epigenetics')

#First we need to drop the index on 'project' 
mongo.drop_index('methylation','project_1')

queryDict = {'sample_label':{'$in':sample_labels_list}}
updateDict = {'$set':{'project':'gecko'}}
mongo.update('methylation', queryDict, updateDict, True)

print "Done updating in ", (time()-t0)

mongo.ensure_index('methylation','project')
