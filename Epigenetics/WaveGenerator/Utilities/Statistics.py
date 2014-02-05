'''
Created on 2013-06-04

@author: afejes

x = (a**2 d+sqrt(a**4 (-b**2) log(b/a)+a**2 b**4 log(b/a)+a**2 b**2 c**2-2 a**2 b**2 c d+a**2 b**2 d**2)-b**2 c)/(a**2-b**2)
where x is the position of the max distance between two CDFs
 with mean c and d, and with standard deviation a and b, respectively.
'''
from math import sqrt, log, erf, fabs

def phi(x):
    '''phi function'''
    return (1.0 + erf(x / sqrt(2.0))) / 2.0

class Kolmogorov_Smirnov(object):
    '''This is a test to compare two empirical distributions to see if they are from the same original function.'''

    @staticmethod
    def ks_test(m1,    # mean of first sample
                s1,    # standard deviation of first sample
                m2,    # mean of second sample
                s2):    # standard deviation of second sample

        '''run the ks test, returns a value that can be interpreted'''
        s1 = float(s1)
        s2 = float(s2)
        m1 = float(m1)
        m2 = float(m2)
        # Check the peaks actually overlap within 4 sigmas...
        start = max(m1 - (4 * s1), m2 - (4 * s2))
        end = min(m1 + (4 * s1), m2 + (4 * s2))
        if start >= end:
            return 1.0    # if the peaks don't overlap, there is no chance of them being related.
        if m1 > m2:
            m1 = m1 - m2
            m2 = 0
        else:
            m2 = m2 - m1
            m1 = 0

        if s1 == s2:    # if sigmas are identical, the greatest difference will always be at the midpoint.
            x = (m1 + m2) / 2.0
            return fabs(phi((x - m1) / s1) - phi((x - m2) / s2))    # the p value at the max distance
        # set up squares required for calculation
        a2 = s1 * s1
        a4 = a2 * a2
        b2 = s2 * s2
        b4 = b2 * b2
        c2 = m1 * m1
        d2 = m2 * m2
        # either m1 or m2 will always be 0, can remove term, may speed up calculation
        # Calculate the point of max distance between CDFs
        # term = (a4 * (-b2) * log(s2 / s1)) + (a2 * b4 * log(s2 / s1)) + (a2 * b2 * c2) - (2 * a2 * b2 * m1 * m2) + (a2 * b2 * d2)  #original
        term = (a4 * (-b2) * log(s2 / s1)) + (a2 * b4 * log(s2 / s1)) + (a2 * b2 * c2) + (a2 * b2 * d2)    # simplified
        # there are two possible solutions for this problem - one will be larger than the other.
        x1 = (a2 * m2 + sqrt(term) - b2 * m1) / (a2 - b2)
        a1 = fabs(phi((x1 - m1) / s1) - phi((x1 - m2) / s2))
        x2 = (a2 * m2 - sqrt(term) - b2 * m1) / (a2 - b2)
        a2 = fabs(phi((x2 - m1) / s1) - phi((x2 - m2) / s2))
        # Return the max distance
        return max(a1, a2)


    def __init__(self, params):
        '''
        Constructor
        '''
        pass

