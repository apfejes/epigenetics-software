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
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters




def AddAnnotations(collection, annotation, Query):
    '''Updates methylation data with annotation information'''
    mongo.ensure_index(annotation, 'array_type')
    mongo.ensure_index(collection, 'probe_id')    # Speed
    fQuery = {'array_type': 'humanmethylation450_beadchip'}
    rQuery = {'TargetID': True, 'Probe_start': True, 'Probe_end': True, 'CHR': True}
    print('Finding annotation information')
    annot_cursor = mongo.find(annotation, findQuery = fQuery, returnQuery = rQuery)

    count = 0
    starttime = time.time()
    print('Updating methylation data with annotation info')
    for annot_doc in annot_cursor:
        queryDict = {'$and': [{'probe_id': annot_doc['TargetID']}, Query]}
        # queryDict = [{'probe_id': annot_doc['TargetID']}, {'annotation_id': {'$exists': False}}]
        updateDict = {'start_position': annot_doc['Probe_start'],
                      'end_position': annot_doc['Probe_end'],
                      'CHR': annot_doc['CHR'],
                      'annotation_id': annot_doc['_id']}
        mongoDict = {'$set': updateDict}
        mongo.update(collection, queryDict, mongoDict)
        count += 1
        if count % 10000 == 0:
            print count, time.time() - starttime, 'seconds'


def AddProjectInfo(mongo, collection, Query, project):
    '''function that adds project information to a sample'''

    print('Adding project info...')
    projDict = {'$set': {'project': project}}
    mongo.update(collection, Query, projDict)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('methylation and annotations collection name must be given.')
        sys.exit()
    collection_name = sys.argv[1]
    annotation_name = sys.argv[2]

    p = Parameters.parameter()
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))

    # database_name = 'human_epigenetics'
    p.set('default_databaset', 'jake_test')
    collection_name = 'methylation'
    annotation_name = 'annotations'
    annotQuery = {'annotation_id': {'$exists': False}}    # Search for un-updated docs (AddAnnotations)
    projQuery = {'project': {'$exists': False}}    # Seach for un-updated docs (AddProjectInfo)

    project_name = raw_input('Enter project name to add to each un-updated document in collection: ')
    print('Adding annotation info to all documents without the field, "annotation_id"...')
    AddAnnotations(mongo, collection_name, annotation_name, annotQuery)
    print('Adding project name to all documents without the field, "project"...')
    AddProjectInfo(mongo, collection_name, projQuery, project_name)


