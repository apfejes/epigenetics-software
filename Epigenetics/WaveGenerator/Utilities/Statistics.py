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

    @staticmethod
    def ks_test(mean1, sigma1, mean2, sigma2):
        sigma1, sigma2, mean1, mean2 = float(sigma1), float(sigma2), float(mean1), float(mean2)
        # Check the pekas actually overlap...
        start1 = mean1 - (4 * sigma1)
        end1 = mean1 + (4 * sigma1)
        start2 = mean2 - (4 * sigma2)
        end2 = mean2 + (4 * sigma2)

        start = max(start1, start2)
        end = min(end1, end2)

        if start > end:
            return (0.0, 0.0)

        # Calculate the point of max distance between CDFs
        a, b, c, d = sigma1, sigma2, mean1, mean2
        a2 = a * a
        a4 = a2 * a2
        b2 = b * b
        b4 = b2 * b2
        c2 = c * c
        d2 = d * d
        x = (a2 * d + sqrt(a4 * (-b2) * log(b / a) + a2 * b4 * log(b / a) + a2 * b2 * c2 - 2 * a2 * b2 * c * d + a2 * b2 * d2) - b2 * c) / (a2 - b2)
        # Find the max distance
        def phi(x):
            return (1.0 + erf(x / sqrt(2.0))) / 2.0

        y = fabs(phi((x - c) / a) - phi((x - d) / b))
        return (x, y)


    def __init__(self, params):
        '''
        Constructor
        '''
        pass

sigma1, sigma2, mean1, mean2 = 3.0, 6.0, 5.0, 3.0
print MyClass(1).ks_test(mean1, sigma1, mean2, sigma2)