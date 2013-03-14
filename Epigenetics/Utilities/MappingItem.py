'''
Created on 2013-03-13

@author: afejes
'''

class item():
    coverage_map = []
    start = 0
    chr = None


    def __init__(self, cov_map, chromosome, start):
        item.coverage_map = cov_map
        item.start = start
        item.chr = chromosome

    def type(self):
        return "MappingItem"
