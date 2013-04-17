'''
Created on 2013-04-15

@author: afejes
'''

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
        curs = self.mongo.find(collection, {"chip":{"$exists": True}}, {"chip": True})
        results = []
        for c in curs:
            results.append(c['chip'])
        return results
