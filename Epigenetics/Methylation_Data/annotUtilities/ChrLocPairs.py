'''
Created on 2013-04-10

@author: jyeung
'''


from collections import defaultdict


class ChrLocPairs(object):
    '''
    A class representing chromosome and location pairs. 
    '''


    def __init__(self, *chr_loc_pairs):
        '''
        *chr_loc_pairs: pairs (in tuple) representing
                        (chromosome, location). 
        '''
        d = defaultdict(list)
        list_pairs = []
        for chromosome, location in chr_loc_pairs:
            d[chromosome].append(location)
            list_pairs.append((chromosome, location))
        self.dic = d
        self.list = list_pairs
        
    def findQuery(self, window=1000):
        '''
        From pairs of Chr:Loc, get query that can be used to search whose
        location are within a specified window.
        Inputs:
            window: find probes within specified distance from
                    location of interest. 
                    The midpoint of window is the location of interest.
        Output:
            A dictionary that can be used as a search query for mongoDB.
        '''
        list_orQuery = []
        for chromo, loc in self.list:
            list_andQuery = []
            dic_andQuery = {}
            
            loc_min = loc - window/2    # What if loc is close to 0?
            loc_max = loc + window/2
            
            dic_chromo = {'chromosome': chromo}
            # dic_loc = {'start_loc': {'$gte': loc_min, '$lte': loc_max}}
            dic_loc = {'start_loc': {'$gte': loc_min, '$lte': loc_max}}
            
            list_andQuery.append(dic_chromo)
            list_andQuery.append(dic_loc)
            dic_andQuery['$and'] = list_andQuery
            print dic_andQuery
            
            list_orQuery.append(dic_andQuery)
        
        mongoFindQuery = {'$or': list_orQuery}
        print mongoFindQuery
        return mongoFindQuery
    
    def returnQuery(self, showid = True):
        '''
        get a returnQuery to specify what keys you want returned from your search
        Inputs:
            id: if True, returns mongoDB ID, change to false to suppress this return. 
        '''
        query_return = {'probe_name': True, '_id': showid, 'start_loc': True, 'chromosome': True}
        return query_return
    
    def findQueryOld(self, window=1000):
        '''
        From pairs of Chr:Loc, get query that can be used to search whose
        location are within a specified window.
        Inputs:
            window: find probes within specified distance from
                    location of interest. 
                    The midpoint of window is the location of interest.
        Output:
            A dictionary that can be used as a search query for mongoDB.
        '''
        list_chromosome = ChrLocPairs.dic.keys()
        # Flatten ChrLocPairs.dic.values() into a single list with no sublist.
        list_location = [item for sublist in ChrLocPairs.dic.values() for item in sublist]
        
        # Create a query combining to search for locations within windows.
        # query_chromosome to search for specified chromosomes. 
        query_list = []
        query_chromosome = {'chromosome': {'$in': list_chromosome}}
        for loc in list_location:
            loc_min = loc - window/2    # What if loc is close to 0?
            loc_max = loc + window/2 
            query_location = {'start_loc': {'$gte': loc_min, '$lte': loc_max}}
            query_list.append(query_location)
        query_list.append(query_chromosome)
        
        query_full = {'$and': query_list}
        return query_full
