"""
Created on 2013-06-04

@author: afejes

x = (a**2 d+sqrt(a**4 (-b**2) log(b/a)+a**2 b**4 log(b/a)+a**2 b**2 c**2-2 a**2
     b**2 c d+a**2 b**2 d**2)-b**2 c)/(a**2-b**2)
where x is the position of the max distance between two CDFs
 with mean c and d, and with standard deviation a and b, respectively.
"""
from math import sqrt, log, erf, fabs

q_test_cutoff = {3: {"Q90": 0.941, "Q95": 0.97, "Q99": 0.994},
                 4: {"Q90": 0.765, "Q95": 0.829, "Q99": 0.926},
                 5: {"Q90": 0.642, "Q95": 0.71, "Q99": 0.821},
                 6: {"Q90": 0.56, "Q95": 0.625, "Q99": 0.74},
                 7: {"Q90": 0.507, "Q95": 0.568, "Q99": 0.68},
                 8: {"Q90": 0.468, "Q95": 0.526, "Q99": 0.634},
                 9: {"Q90": 0.437, "Q95": 0.493, "Q99": 0.598},
                 10: {"Q90": 0.412, "Q95": 0.466, "Q99": 0.568}}


def phi(x):
    '''phi function'''
    return (1.0 + erf(x / sqrt(2.0))) / 2.0


def lower_Qtest(numbers, qvalue):

    numbers.sort()
    l = len(numbers)
    if l < 3:
        return False, None
    if numbers[l - 1] - numbers[0] == 0:
        return False, None
    test1 = (numbers[1] - numbers[0]) / (numbers[l - 1] - numbers[0])
    if l > 10:
        l = 10
    if test1 > q_test_cutoff[l][qvalue]:
        return True, numbers[1:]    # it is an outlier
    return False, None


def upper_Qtest(numbers, qvalue):
    numbers.sort()
    l = len(numbers)
    if l < 3:
        return False, None
    if numbers[l - 1] - numbers[0] == 0:
        return False, None
    test2 = (numbers[l - 1] - numbers[l - 2]) / (numbers[l - 1] - numbers[0])
    if l > 10:
        l = 10
    if test2 > q_test_cutoff[l][qvalue]:
        return True, numbers[:-1]
    return False, None


class Kolmogorov_Smirnov(object):
    """This is a test to compare two empirical distributions to see if
     they are from the same original function."""

    @staticmethod
    def ks_test(m1,    # mean of first sample
                s1,    # standard deviation of first sample
                m2,    # mean of second sample
                s2):    # standard deviation of second sample

        """run the ks test, returns a value that can be interpreted"""
        s1 = float(s1)
        s2 = float(s2)
        m1 = float(m1)
        m2 = float(m2)
        # Check the peaks actually overlap within 4 sigmas...
        start = max(m1 - (4 * s1), m2 - (4 * s2))
        end = min(m1 + (4 * s1), m2 + (4 * s2))
        if start >= end:
            return 1.0    # if the peaks don't overlap, there is no chance
                            # of them being related.
        if m1 > m2:
            m1 -= m2
            m2 = 0
        else:
            m2 -= m1
            m1 = 0

        if s1 == s2:    # if sigmas are identical, the greatest difference
                        # will always be at the midpoint.
            x = (m1 + m2) / 2.0
            return fabs(phi((x - m1) / s1) - phi((x - m2) / s2))    # the p value at the max distance
        # set up squares required for calculation
        a2 = s1 * s1
        a4 = a2 * a2
        b2 = s2 * s2
        b4 = b2 * b2
        c2 = m1 * m1
        d2 = m2 * m2
        # either m1 or m2 will always be 0, can remove term,
        # may speed up calculation
        # Calculate the point of max distance between CDFs
        # term = (a4 * (-b2) * log(s2 / s1)) + (a2 * b4 * log(s2 / s1)) +
        # (a2 * b2 * c2) - (2 * a2 * b2 * m1 * m2) + (a2 * b2 * d2)  #original
        term = (a4 * (-b2) * log(s2 / s1)) + (a2 * b4 * log(s2 / s1)) \
               + (a2 * b2 * c2) + (a2 * b2 * d2)    # simplified
        # there are two possible solutions for this problem -
        # one will be larger than the other.
        x1 = (a2 * m2 + sqrt(term) - b2 * m1) / (a2 - b2)
        a1 = fabs(phi((x1 - m1) / s1) - phi((x1 - m2) / s2))
        x2 = (a2 * m2 - sqrt(term) - b2 * m1) / (a2 - b2)
        a2 = fabs(phi((x2 - m1) / s1) - phi((x2 - m2) / s2))
        # Return the max distance
        return max(a1, a2)

    def __init__(self, params):

        """
        Constructor
        """
        pass

