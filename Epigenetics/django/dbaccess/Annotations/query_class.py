#from collections import OrderedDict #with Python 2.7 and above

class MongoQuery():
    ''' A class to store the information from a user's query.
        An instance of this class is a dictionary with immutable keys but
        mutable values
        '''
        
    def __init__(self):
        #print "This is an instance of the MongoQuery dictionary class."
        #print "Use the elements() method to print the query data."
        
        fixed_dictionary = {"database":None, "collection": None, 
                            "sample type":None, "chromosome":None, 
                            "start" : None, "end" : None,
                            "sample label" : None, "project" : None,
                            "docs" : None, "waves" : None}
        
        self._data = fixed_dictionary
        
    def __setitem__(self, key, value):
        if key not in self._data:
            raise KeyError("The key {} is not defined.".format(key))
        self._data[key] = value
        
    def __getitem__(self, key):
        return self._data[key]


    def __str__(self):
        # FORMAT ME!
        output = "This query has the following elements: \n 	"
        output += self._data.__str__()
        lines = 0
        for key, value in self._data.iteritems():
            if lines%3==0 and lines > 0: output += "\n	"
            output += key + " : " + format(value) + ", "
            lines +=1
        return output
    
    
k = MongoQuery()
k['database'] = "hello"
k['collection'] = "world"
k["sample"]=9
k["start"]=1000
k["end"]=12
k["chromosome"]="chr4"
print k
