'''
Created on 2013-06-04

@author: afejes
'''

class MyClass(object):
    '''
    classdocs
    '''

    def ks_test(self, mean1, sigma1, mean2, sigma2):
        p = 0
        start1 = mean1 - (4 * sigma1)
        end1 = mean1 + (4 * sigma1)
        start2 = mean2 - (4 * sigma2)
        end2 = mean2 + (4 * sigma2)

        start = max(start1, start2)
        end = min(end1, end2)

        if start > end:
            return 0

        return p



    def __init__(self, params):
        '''
        Constructor
        '''
        pass
