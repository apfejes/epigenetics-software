'''
Created on 2013-03-31

@author: jyeung
'''


class Cursor(object):
    '''
    A class of objects that represents data retrieval from mongoDB.
    The functions give only Cursor objects, not the documents themeslves. 
    Iterating through the Cursor objects will interact with mongoDB and
    return the documents. 
    '''


    def __init__(self, collection):
        '''
        Initialize with collection object. This collection object should
        already be connected with mongoDB (e.g. db.collection)
        '''
        self.collection = collection
        print('{0}{1}'.format('Currently in collection: ',
                              self.collection.name))

    def GetProbesInChromosome(self, *chromosomes):
        '''
        This will get probe annotation data of where each probe is in the 
        chromosome. Therefore, this will ignore probes not mapped to a
        chromosome. 
        
        Inputs:
        chromosome*: chromosomes you want to search for.
                     example: GetProbesInChromosome(1, 2, 3) will retrieve
                     probes from chromosomes 1, 2, 3. 
                     
        Outputs:
        dictionary of probenames (key) and where it is on chromosome (value)
        
        First, create a list of chromosomes to search for from input. 
        Second, search mongo within collection, get chromosome and probename
        Third, creates and returns a list of probenames in that chromosome. 
        '''

        # 1.
        chromosome_list = []    # Initialize list chromosome
        for chromosome in chromosomes:
            chromosome_list.append(str(chromosome))

        # 2.
        print('{0}{1}'.format('Finding probes in chromosome(s): ',
                                 str(chromosome_list)))
        fData = self.collection.find({'MAPINFO': {'$in': chromosome_list}},
                                {'MAPINFO': True, 'NAME': True, '_id': False})
        print('{0}{1}'.format(fData.count(), ' annotation documents found.'))

        # 3.

        probe_dict = {}    # Initialize dictionary
        for dat in fData:
            probe_dict[dat['NAME']] = dat['MAPINFO']
        return(probe_dict)


    def GetBetasFromProbes(self, probe_list):
        '''
        From a list of probes, returns the corresponding beta values within
        that collection. 
        
        Inputs:
        probe_list: a list of probes for which you want to fin betas.
                     
        Outputs:
        a pymongo.cursor.Cursor object that can be iterated to get dictionary
        containing key:value pairs of probename, betavalue and samplename. 
        '''
        print('{0}{1}'.format('Getting cursor from probelist size of ',
                              len(probe_list)))
        documents = self.collection.find({'$and':[{'probe_name': {'$in': probe_list}},
                                                 {'beta_value': {'$exists': True}}]},
                                         {'probe_name': True,
                                          'beta_value': True,
                                          'sample_name': True,
                                          '_id': False})
        print('{0}{1}'.format(documents.count(), ' documents found.'))
        return(documents)


    def GetDocsWithKeys(self, *keys):
        '''
        Get docs containing keys.
        
        Inputs:
        *keys: finds all documents in collection where these keys exist. 
               inputs should be strings. 
                     
        Outputs:
        a pymongo.cursor.Cursor object that can be iterated to get dictionary
        containing key:value pairs
        '''
        print('{0}{1}'.format('Finding docs containing: ',
                              str(keys)))
        key_set = []    # Initialize
        for key in keys:
            dic = {}    # Initialize
            dic[key] = {'$exists': True}
            key_set.append(dic)
        query = {'$or': key_set}
        docs = self.collection.find(query, {'_id': False})
        print('{0}{1}{2}'.format(docs.count(), ' documents retrieved with keys: ',
                              str(keys)))
        return docs


    def GetDocsOneKey(self,):
        pass
