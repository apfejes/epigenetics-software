'''

Template code for deprecated function from http://wiki.python.org/moin/PythonDecoratorLibrary
Created on 2013-08-23

@author: afejes
'''

import warnings


class Decorators(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
    @staticmethod
    def deprecated(func):
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emmitted
        when the function is used."""
        def newFunc(*args, **kwargs):
            warnings.warn("Call to deprecated function %s." % func.__name__,
                          category = DeprecationWarning)
            return func(*args, **kwargs)
        newFunc.__name__ = func.__name__
        newFunc.__doc__ = func.__doc__
        newFunc.__dict__.update(func.__dict__)
        return newFunc
