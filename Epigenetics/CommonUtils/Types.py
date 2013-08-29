'''
Created on Aug 26, 2013

@author: afejes
'''

def is_int(s):
    '''test if a variable is an integer or not.'''
    try:
        int(s)
        return True
    except ValueError:
        return False