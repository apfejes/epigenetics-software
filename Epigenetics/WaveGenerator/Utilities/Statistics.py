'''
Created on 2013-06-04

@author: afejes


Using Wolfram alpha, get the solution:
x = (a**2 d+sqrt(a**4 (-b**2) log(b/a)+a**2 b**4 log(b/a)+a**2 b**2 c**2-2 a**2 b**2 c d+a**2 b**2 d**2)-b**2 c)/(a**2-b**2)
where x is the position of the max distance between two CDFs
 with mean c and d, and with standard deviation a and b, respectively.
'''
from math import sqrt, log, erf, fabs

class MyClass(object):
    '''
    classdocs
    '''

    def ks_test(self, mean1, sigma1, mean2, sigma2):
        
        #Check the pekas actually overlap...
        start1 = mean1 - (4 * sigma1)
        end1 = mean1 + (4 * sigma1)
        start2 = mean2 - (4 * sigma2)
        end2 = mean2 + (4 * sigma2)

        start = max(start1, start2)
        end = min(end1, end2)

        if start > end:
            return 0

        #Calculate the point of max distance between CDFs
        a,b,c,d = sigma1,sigma2,mean1,mean2
        x = (a**2*d+sqrt(a**4*(-b**2)*log(b/a)+a**2*b**4*log(b/a)+a**2*b**2*c**2-2*a**2*b**2*c*d+a**2*b**2*d**2)-b**2*c)/(a**2-b**2)
        #Find the max distance
        def phi(x):
            return (1.0 + erf(x / sqrt(2.0))) / 2.0

        y = fabs(phi((x-c)/a)-phi((x-d)/b))
        return (x, y)


    def __init__(self, params):
        '''
        Constructor
        '''
        pass
