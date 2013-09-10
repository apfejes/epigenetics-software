'''
Created on 2013-03-13

@author: afejes
'''
import sys
import CommonUtils.Types as cu


class parameter(object):
    '''
    classdocs
    '''

    def __init__(self, filename):
        '''
        Constructor
        '''
        self.parameters = {}
        try:
            f = open(filename, 'r')
            for line in f:
                if line.startswith("#"):
                    continue
                else:
                    a = line.split("=")
                    key = a[0].strip()
                    value = a[1].strip()
                    # print "read:", key, "->", value
                    if cu.is_int(value):    # handle ints
                        self.parameters[key] = int(value)
                    elif cu.is_float(value):    # handle floats
                        self.parameters[key] = float(value)
                    elif cu.is_bool(value):    # handle booleans
                        if (value.lower() == "true"):
                            self.parameters[key] = True
                        else:
                            self.parameters[key] = False
                    else:    # handle strings
                        self.parameters[key] = value

            f.close()
        except:
            print "Unexpected error in parameter reading:", sys.exc_info()[0]
            print "Reading parameters failed."
            print ""
            sys.exit()

    def set_parameter(self, key, value):
        '''set a parameter with a key value pair'''
        self.parameters[key] = value

    def get_parameter(self, key):
        '''get a parameter with a key value'''
        if (self.parameters.has_key(key)):
            return self.parameters.get(key)
        else:
            print "invalid lookup of key:", key
            return None

    @staticmethod
    def type():
        '''Simply return "Parameter List" when asked'''
        return ("Parameter List")
