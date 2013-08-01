'''
Created on 2013-04-15

@author: afejes
'''

def CreateListFromCursor(cursor):
    listitems = []
    for record in cursor:
        listitems.append(record)
    return listitems


class MongoUtilities(object):
    '''
    classdocs
    '''


    def __init__(self, mongo):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.mongo = mongo

    def get_chip_seq_sample_names(self):
        collection = "samples"
        curs = self.mongo.find(collection, {"chip":{"$exists": True}}, {"cell_line": True, "chip": True})
        results = []
        for c in curs:
            results.append("%s - %s" % (c['cell_line'], c['chip']))
        return results

    def get_chromosome_names(self):
        collection = "chromosomes"
        curs = self.mongo.find(collection, {"_id":{"$exists": True}})
        results = []
        for c in curs:
            results.append(c['_id'])
        return results

    def get_sample_id_from_name(self, name):
        collection = "samples"
        results = []
        if " - " in name:
            parts = name.split(" - ")
        curs = self.mongo.find(collection, {"cell_line": parts[0], "chip": parts[1]}, {"_id": True})
        for c in curs:
            results.append(c['_id'])
        return results
