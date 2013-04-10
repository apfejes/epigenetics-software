'''
Created on 2013-04-09

@author: jyeung
'''


import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


class ListVector(object):
    '''
    A class of objects that are string vectors from R. 
    '''


    def __init__(self, ListVector):
        '''
        List vector that was generated from R.
        '''
        self.list = ListVector
    
    def names(self):
        namesR = robjects.r['names']
        names_of_list = namesR(self.list)
        return names_of_list
        
    def unlist(self):
        unlistR = robjects.r['unlist']
        self.unlist = unlistR(self.list)
    
    def subnames(self):
        namesR = robjects.r['names']
        unlistR = robjects.r['unlist']
        unlisted = unlistR(self.list)
        subnames_of_list = namesR(unlisted)
        return subnames_of_list
    

        
        