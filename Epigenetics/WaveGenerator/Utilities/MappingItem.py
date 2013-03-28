'''
Created on 2013-03-13

@author: afejes
'''

class Item():

    def __init__(self, cov_map, chromosome, start):
        self.coverage_map = cov_map
        self.start = start
        self.chr = chromosome

    def type(self):
        return "MappingItem"
