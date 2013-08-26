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

    def get_left_end(self):
        '''simple getter function for the left_end coordinate'''
        return self.left_end

    def get_right_end(self):
        '''simple getter function for the right_end coordinate'''
        return self.right_end

    def get_read(self):
        '''simple getter function for the read object itself.'''
        return self.read

    @staticmethod
    def type():
        '''Display AlignedReadObj when asked the type'''
        return "AlignedReadObj"

