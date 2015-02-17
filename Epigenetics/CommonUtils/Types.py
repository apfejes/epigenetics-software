"""
Created on Aug 26, 2013

@author: afejes
"""


def is_int(s):
    """Test if element is an integer, by trying to convert to int.
    If it can't be done, it's not an int"""
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(element):
    """Test if element is a float, by trying to convert to float.
    If it can't be done, it's not an float"""
    try:
        float(element)
    except ValueError:
        return False
    return True


def is_bool(element):
    """Test if element is a boolean variable by checking if it
    is a string that says either true or false"""
    if element.lower() == "true" or element.lower() == "false":
        return True
    else:
        return False
