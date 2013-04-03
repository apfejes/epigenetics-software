'''
Created on 2013-03-31

@author: jyeung
'''


from pymongo import MongoClient


class Cursor(object):
    '''
    A class containing mongo documents that can be iterated to get individual
    dictionaries corresponding to a mongoDB entry.
    '''


    def __init__(self, cursor):
        '''
        documents is the output of a mongodb.collection.find() command.
        Create a new Cursor instance. 
        '''
        self.cursor = cursor.clone()
        self.doc = None
        
        
    def cursor(self):
        self.cursor = cursor.clone()
        return self


    def GetValuesFromKey(self, keyname):
        '''
        Get list from keyname of documents. 
        Inputs: keyname such as 'SampleID'
        Outputs: list of values for that keyname. 
        '''
        self.cursor = self.cursor.clone()    # In case cursor's depleted
        list_values = []    # Initialize
        for doc in self.cursor:
            list_values.append(doc[keyname])
        return(list_values)
        
        
    def GetDocsKeyname(self, keyname):
        '''
        Get docs from this cursor that contain the keyname you want.
        This is almost like filtering.  
        '''
        pass
        self.cursor = self.cursor.clone()    # In case cursor's depleted.
        for doc in self.cursor:
            pass
        
            