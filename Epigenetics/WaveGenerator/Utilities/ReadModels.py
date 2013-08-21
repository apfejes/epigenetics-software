'''
Created on 2013-03-06

@author: afejes
'''



class Distribution():

    def __init__(self):
        '''constructor'''
        pass

    @staticmethod
    def Flat(length):
        a = [1] * length
        return a

    @staticmethod
    def Triangle(min_point, med_point, max_point):
        a = [1.0] * max_point
        for i in range(min_point, med_point):
            a[i] = 1.0 - (0.5 * ((float(i) - min_point) / (float(med_point) - min_point)))
        for i in range(med_point, max_point):
            a[i] = 0.5 - (0.5 * (float(i) - med_point) / (float(max_point) - med_point))
        return a

    @staticmethod
    def round_leading_edge(array):
        d = 25
        for i in xrange(d):
            array[i] = (i + 1) / (d + 1)
        return array

