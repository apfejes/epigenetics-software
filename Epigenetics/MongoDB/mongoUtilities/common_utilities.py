'''
Created on 2013-04-15

@author: afejes
'''

import gc


def CreateListFromCursor(cursor):
    '''convert a cursor to a full list of items'''
    gc.disable()
    listitems = []
    if cursor is None:
        return {}
    for record in cursor:
        listitems.append(record)
    gc.enable()
    return listitems

def CreateListFromOIDs(cursor):
    '''convert a cursor of objectIDs to a full list of items'''
    gc.disable()
    listitems = []
    if cursor is None:
        return {}
    for record in cursor:
        listitems.append(str(record['_id']))
    gc.enable()
    return listitems



class MongoUtilities(object):
    '''TODO:missing docstring'''


    def __init__(self, mongo):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.mongo = mongo

    def get_chip_sample_names(self):
        '''TODO:missing docstring'''
        collection = "samples"
        curs = self.mongo.find(collection, {"haswaves":{"$exists": True}}, {"sample_id": True}).sort("sample_id", 1)
        results = []
        for c in curs:
            results.append("%s" % c['sample_id'])
        return results

    def get_chromosome_names(self):
        '''TODO:missing docstring'''
        collection = "chromosomes"
        curs = self.mongo.find(collection, {"_id":{"$exists": True}})
        results = []
        for c in curs:
            results.append(c['_id'])
        return results

    def get_sample_id_from_name(self, name, db):
        '''TODO:missing docstring'''
        collection = "samples"
        results = []
        if db == "yeast_epigenetics":
            curs = self.mongo.find(collection, {"sample_id":name}, {"_id": True})
        else:
            # not sure if this works...
            if " - " in name:
                parts = name.split(" - ")
            curs = self.mongo.find(collection, {"cell_line": parts[0], "chip": parts[1]}, {"_id": True})

        for c in curs:
            results.append(c['_id'])
        return results
