'''
Created on 2013-01-28

@author: fejes
'''

class AlignedReadObj():

    def __init__(self, le, re, read):
        self.left_end = le
        self.right_end = re
        self.read = read

    def get_left_end(self):
        return self.left_end

    def get_right_end(self):
        return self.right_end

    def get_read(self):
        return self.read

    def type(self):
        return "AlignedReadObj"

