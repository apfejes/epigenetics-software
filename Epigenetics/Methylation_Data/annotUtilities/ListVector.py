'''
Created on 2013-04-09

@author: jyeung
'''


import rpy2.robjects as robjects


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
    
    def subname(self, index):
        namesR = robjects.r['names']
        sublist = self.list.rx2(index)
        names_of_sublist = namesR(sublist)
        return names_of_sublist[0]
    

        
        