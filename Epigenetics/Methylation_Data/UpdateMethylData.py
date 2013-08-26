'''
Created on 2013-04-15

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


# database_name = 'human_epigenetics'
database_name = 'jake_test'
collection_name = 'methylation'
annotation_name = 'annotations'
annotQuery = {'annotation_id': {'$exists': False}}    # Search for un-updated docs (AddAnnotations)
projQuery = {'project': {'$exists': False}}    # Seach for un-updated docs (AddProjectInfo)
# project_name = 'kollman'
# project_name = 'down'


def AddAnnotations(collection_name, annotation_name, annotQuery):
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    mongo.ensure_index(annotation_name, 'array_type')
    mongo.ensure_index(collection_name, 'probe_id')    # Speed
    fQuery = {'array_type': 'humanmethylation450_beadchip'}
    rQuery = {'TargetID': True, 'Probe_start': True, 'Probe_end': True, 'CHR': True}
    print('Finding annotation information')
    annot_cursor = mongo.find(annotation_name, findQuery = fQuery, returnQuery = rQuery)

    count = 0
    starttime = time.time()
    print('Updating methylation data with annotation info')
    for annot_doc in annot_cursor:
        queryDict = {'$and': [{'probe_id': annot_doc['TargetID']}, annotQuery]}
        # queryDict = [{'probe_id': annot_doc['TargetID']}, {'annotation_id': {'$exists': False}}]
        updateDict = {'start_position': annot_doc['Probe_start'],
                      'end_position': annot_doc['Probe_end'],
                      'CHR': annot_doc['CHR'],
                      'annotation_id': annot_doc['_id']}
        mongoDict = {'$set': updateDict}
        mongo.update(collection_name, queryDict, mongoDict)
        count += 1
        if count % 10000 == 0:
            print count, time.time() - starttime, 'seconds'


def AddProjectInfo(collection_name, projQuery, project_name):
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    print('Adding project info...')
    projDict = {'$set': {'project': project_name}}
    mongo.update(collection_name, projQuery, projDict)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('methylation and annotations collection name must be given.')
        sys.exit()
    collection_name = sys.argv[1]
    annotation_name = sys.argv[2]
    project = raw_input('Enter project name to add to each un-updated document in collection: ')
    print('Adding annotation info to all documents without the field, "annotation_id"...')
    AddAnnotations(collection_name, annotation_name, annotQuery)
    print('Adding project name to all documents without the field, "project"...')
    AddProjectInfo(collection_name, projQuery, project)


