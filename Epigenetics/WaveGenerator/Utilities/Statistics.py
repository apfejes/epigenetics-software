'''
Created on 2013-06-04

@author: afejes


Using Wolfram alpha, get the solution:
x = (a**2 d+sqrt(a**4 (-b**2) log(b/a)+a**2 b**4 log(b/a)+a**2 b**2 c**2-2 a**2 b**2 c d+a**2 b**2 d**2)-b**2 c)/(a**2-b**2)
where x is the position of the max distance between two CDFs
 with mean c and d, and with standard deviation a and b, respectively.
'''
from math import sqrt, log, erf, fabs

def phi(x):
        return (1.0 + erf(x / sqrt(2.0))) / 2.0

class MyClass(object):
    '''
    classdocs
    '''

    @staticmethod
    def ks_test(mean1, sigma1, mean2, sigma2):
        sigma1, sigma2, mean1, mean2 = float(sigma1), float(sigma2), float(mean1), float(mean2)
        # Check the peaks actually overlap...
        start1 = mean1 - (4 * sigma1)
        end1 = mean1 + (4 * sigma1)
        start2 = mean2 - (4 * sigma2)
        end2 = mean2 + (4 * sigma2)

        start = max(start1, start2)
        end = min(end1, end2)

        if start > end:
            return (0.0, 0.0)

        if mean1 > mean2:
            mean1 = mean1 - mean2
            mean2 = 0
        else:
            mean2 = mean2 - mean1
            mean1 = 0

        # Calculate the point of max distance between CDFs
        a, b, c, d = sigma1, sigma2, mean1, mean2
        a2 = a * a
        a4 = a2 * a2
        b2 = b * b
        b4 = b2 * b2
        c2 = c * c
        d2 = d * d
        # print "(b/a) %f" % (b / a)
        # print "log(b/a) %f" % log(b / a)
        term = (a4 * (-b2) * log(b / a)) + (a2 * b4 * log(b / a)) + (a2 * b2 * c2) - (2 * a2 * b2 * c * d) + (a2 * b2 * d2)

        if a == b:
            x = (c + d) / 2
        elif a > b:

                x = (a2 * d + sqrt(term) - b2 * c) / (a2 - b2)
        elif b > a:
                x = (a2 * d - sqrt(term) - b2 * c) / (a2 - b2)
        # Return the max distance
        return fabs(phi((x - c) / a) - phi((x - d) / b))



    def __init__(self, params):
        '''
        Constructor
        '''
        pass


# for i in range (0, 40, 5):
#    for j in range (10, 100, 10):
#
#       print " ", j, i
#        x, y = MyClass(1).ks_test(mean1, sigma1, mean2, sigma2)
#        print "    ", x, y

