'''
Mongo Query

'''

# from collections import OrderedDict #with Python 2.7 and above

class MongoQuery():
    ''' A class to store the information from a user's query.
        An instance of this class is a dictionary with immutable keys but
        mutable values
        '''

    def __init__(self):
        # print "This is an instance of the MongoQuery dictionary class."
        # print "Use the elements() method to print the query data."

        fixed_dictionary = {"database":None, "collection": None,
                            "sample type":None, "chromosome":None,
                            "start" : None, "end" : None, "sample_dictionary":None,
                            "sample label" : None, "sample group" : None,
                            "project" : None, "cursor" : None, "waves" : None,
                            "sample id": None, 'sample label list':None}
        self._data = fixed_dictionary

    def __setitem__(self, key, value):
        if key not in self._data:
            raise KeyError("The key {} is not defined.".format(key))
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __str__(self):
        # FORMAT ME!
        output = "\nThis query has the following elements: {\n    "
        # output += self._data.__str__()
        lines = 0
        for key, value in self._data.iteritems():
            if value != None:
                if lines % 2 == 0 and lines > 0:
                    output += "\n    "
                output += key + " : " + format(value) + ", "
                lines += 1
        output += "\n    }"
        return output

    def __repr__(self):
        return "This is an instance of MongoQuery: stores query parameters and data."

