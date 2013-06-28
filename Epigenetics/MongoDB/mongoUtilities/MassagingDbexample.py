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
import Mongo_Connector
import MongoQuery


m = MongoCurious.MongoCurious(database = "human_epigenetics")

sample_query = m.query(collection = "samples", project = 'gecko')
docs = m.finddocs()

sample_labels_list = [doc['sample_label'] for doc in docs]

for doc in docs:
    queryDict = {'sample_label':doc['sample_label']}
    updateDict = {'project':'gecko'}
    Mongo_Connector.update(self, 'methylation', queryDict, updateDict, multiOpt = True)

m.query(collection = 'methylation', project = 'gecko')
print len(m.finddocs())