'''
Created on 2013-03-13

@author: afejes
'''
import sys
import traceback



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
                    if parameter.isint(value):    # handle ints
                        self.parameters[key] = int(value)
                    elif parameter.isfloat(value):    # handle floats
                        self.parameters[key] = float(value)
                    elif parameter.isbool(value):    # handle booleans
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
            print traceback.format_exc()
            sys.exit()



    def set_parameter(self, key, value):
        self.parameters[key] = value

    def get_parameter(self, key):
        if (self.parameters.has_key(key)):
            return self.parameters.get(key)
        else:
            print "invalid lookup of key:", key
            return None

    @staticmethod
    def isfloat(element):
        try:
            float(element)
        except ValueError:
            return False
        return True

    @staticmethod
    def isint(element):
        try:
            int(element)
        except ValueError:
            return False
        return True

    @staticmethod
    def isbool(element):
        if (element.lower() == "true" or element.lower() == "false"):
            return True
        else:
            return False


    def type(self):
        return ("Parameter List")
