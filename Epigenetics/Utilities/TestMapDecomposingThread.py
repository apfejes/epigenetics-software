'''
Created on 2013-03-15

@author: afejes
'''
import unittest
from Utilities import MapDecomposingThread
import copy


class Test(unittest.TestCase):




    def testBuild_and_destroy(self):
        mapdecomp = MapDecomposingThread.MapDecomposer(None, None, None, None, None)
        length = 90
        height = 15
        sigma = 15
        mu = 45
        coverage_map = [0] * length
        peak = mapdecomp.gausian_value_at_peak(sigma)
        for x in xrange(length):
            coverage_map[x] = (mapdecomp.gausian_value_at_x(sigma, mu, x) / peak) * height
            self.assert_(coverage_map[x] <= height, "creating wave heights larger than anticipated")
            self.assert_(coverage_map[x] >= 0, "creating waves smaller than anticipated")
        # print mapdecomp.print_array(coverage_map)
        coverage_map = mapdecomp.subtract_gausian(coverage_map, height, sigma, mu)
        self.assertEqual(length, len(coverage_map), "lengths after subtract_gausian not conserved")
        # print mapdecomp.print_array(coverage_map)
        for x in xrange(len(coverage_map)):
            self.assert_(coverage_map[x] == 0.0, "Subtraction failed: " + str(coverage_map[x]))

    def testFind_best_sigma(self):
        mapdecomp = MapDecomposingThread.MapDecomposer(None, None, None, None, None)
        height = 15
        sigma = 15
        mu = 45
        coverage_map = [0] * 90
        peak = mapdecomp.gausian_value_at_peak(sigma)
        for x in xrange(90):
            coverage_map[x] = (mapdecomp.gausian_value_at_x(sigma, mu, x) / peak) * height
        s = mapdecomp.best_fit_test(coverage_map, mu, height)
        self.assertEqual(s, sigma, "sigma returned by best fit is incorrect.  expected "
                         + str(sigma) + " got " + str(s))



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
