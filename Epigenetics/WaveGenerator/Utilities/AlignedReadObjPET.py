'''
Created on 2013-01-28

@author: fejes
'''

class AlignedReadObjPET():
    '''An object to hold PET aligned read objects, mainly from BAM files'''

    def __init__(self, chr_id, le, re, read1, read2):
        '''Create the object, store coordinates and reads'''
        self.left_end = le
        self.right_end = re
        self.chromosome_id = chr_id
        self.read1 = read1
        self.read2 = read2


    @staticmethod
    def type():
        '''return AlignedReadObjPET as a string when asked what type of object this is'''
        return "AlignedReadObjPET"

    def is_pet(self):
        '''Test to see if it is actually a pair, that is to say, holding two reads instead of just one.'''
        if self.read2 is None:
            return False
        else:
            return True


