'''
Created on 2013-03-15

@author: afejes
'''
import unittest
from Utilities import MapDecomposingThread


class Test(unittest.TestCase):




    def testName(self):
        mapdecomp = MapDecomposingThread.MapDecomposer(None, None)

        height = 15
        sigma = 15
        mu = 45
        coverage_map = [0] * 90
        peak = mapdecomp.gausian_value_at_peak(sigma)
        for x in xrange(90):
            coverage_map[x] = (mapdecomp.gausian_value_at_x(sigma, mu, x) / peak) * height
        # print mapdecomp.print_array(coverage_map)
        coverage_map = mapdecomp.subtract_gausian(coverage_map, height, sigma, mu)
        # print mapdecomp.print_array(coverage_map)
        for x in xrange(90):
            self.assert_(coverage_map[x] < 0.05, "Subtraction failed")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
