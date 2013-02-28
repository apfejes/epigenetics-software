'''
Created on 2013-01-28

@author: fejes
'''

class AlignedReadObjPET():
    #left_end = 0
    #right_end = 0
    
    def __init__(self, chr_id, le, re, read1, read2):
        self.left_end = le
        self.right_end = re
        self.chromosome_id = chr_id
        self.read1 = read1
        self.read2 = read2
       
    def get_left_end(self):
        return self.left_end
     
    def get_right_end(self):
        return self.right_end
    
    def get_read1(self):
        return self.read1
    
    def get_read2(self):
        return self.read2      
      
    def type(self):
        return "AlignedReadObjPET"
    
    def is_pet(self):
        if self.read2 == None:
            return False
        else:
            return True
    

