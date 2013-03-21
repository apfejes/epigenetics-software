'''
Created on 2013-03-13

@author: afejes
'''


class parameter(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.parameters = {}

    def set_parameter(self, key, value):
        self.parameters[key] = value

    def get_parameter(self, key):
        if (self.parameters.has_key(key)):
            return self.parameters.get(key)
        else:
            print "invalid lookup of key:", key
            return None

    def type(self):
        return ("Parameter List")
