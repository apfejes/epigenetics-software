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
    def ks_test(m1,    # m1
                s1,    # s1
                m2,    # m2
                s2):    # s2

        '''run the ks test, returns a value that can be interpreted'''
        s1 = float(s1)
        s2 = float(s2)
        m1 = float(m1)
        m2 = float(m2)
        # Check the peaks actually overlap within 4 sigmas...

        start = max(m1 - (4 * s1), m2 - (4 * s2))
        end = min(m1 + (4 * s1), m2 + (4 * s2))

        if start > end:
            # return (0.0, 0.0)
            return 0.0

        if m1 > m2:
            m1 = m1 - m2
            m2 = 0
        else:
            m2 = m2 - m1
            m1 = 0

        # Calculate the point of max distance between CDFs

        a2 = s1 * s1
        a4 = a2 * a2
        b2 = s2 * s2
        b4 = b2 * b2
        c2 = m1 * m1
        d2 = m2 * m2
        # term = (a4 * (-b2) * log(s2 / s1)) + (a2 * b4 * log(s2 / s1)) + (a2 * b2 * c2) - (2 * a2 * b2 * m1 * m2) + (a2 * b2 * d2)
        # either m1 or m2 will always be 0, can remove term, may speed up calculation
        term = (a4 * (-b2) * log(s2 / s1)) + (a2 * b4 * log(s2 / s1)) + (a2 * b2 * c2) + (a2 * b2 * d2)

        if s1 == s2:
            x = (m1 + m2) / 2
        elif s1 > s2:

            x = (a2 * m2 + sqrt(term) - b2 * m1) / (a2 - b2)
        elif s2 > s1:
            x = (a2 * m2 - sqrt(term) - b2 * m1) / (a2 - b2)
        # Return the max distance
        return fabs(phi((x - m1) / s1) - phi((x - m2) / s2))



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

