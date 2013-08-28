'''
Created on 2013-01-28

@author: fejes
'''

class AlignedReadObj():
    '''simple class to hold an aligned read object'''

    def __init__(self, le, re, read):
        '''initialize the object to hold the read along with left and right side coordinates'''
        self.left_end = le
        self.right_end = re
        self.read = read


    @staticmethod
    def type():
        '''Display AlignedReadObj when asked the type'''
        return "AlignedReadObj"

