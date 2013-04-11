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
        for chromosome, location in chr_loc_pairs:
            d[chromosome].append(location)
        ChrLocPairs.dic = d.items()
    
    def GetQuery(self, db_name, collection_name, window):
        '''
        From pairs of Chr:Loc, get query that can be used to search 
        '''
        
        
            
        
        