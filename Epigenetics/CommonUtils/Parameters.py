'''
Created on 2013-03-13

@author: afejes
'''
import os
import sys
import CommonUtils.Types as cu


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("CommonUtils" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)

class parameter(object):
    '''
    classdocs
    '''

    def __init__(self, filename = None):
        '''
        Constructor
        '''
        self.parameters = {}
        self.defaults_database()    # set default database parameters
        if filename:
            self.parse_file(filename)    # use files to override defaults and new parameters


    def parse_file(self, filename):
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
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print "Unexpected error in parameter reading:", sys.exc_info()[0]
            print "Reading parameters failed."
            print ""
            sys.exit()


    def set(self, key, value):
        '''set a parameter with a key value pair'''
        self.parameters[key] = value

    def get(self, key, default = None):
        '''get a parameter with a key value
           used to override default behavior of simple get on the parameter object.'''
        if (self.parameters.has_key(key)):
            return self.parameters.get(key)
        elif default:
            return default
        else:
            print "invalid lookup of key:", key
            return None


    def defaults_database(self):
        '''load default database parameters, if the defaults exist.'''
        default_file_location = _root_dir + os.sep + "MongoDB" + os.sep + "database.conf"
        if os.path.exists(default_file_location):
            self.parse_file(default_file_location)


    @staticmethod
    def type():
        '''Simply return "Parameter List" when asked'''
        return ("Parameter List")
