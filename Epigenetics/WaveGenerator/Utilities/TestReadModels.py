'''
Created on 2013-03-06

@author: afejes
'''
import unittest
import ReadModels

class Test(unittest.TestCase):


    def testFlat(self):
        a = ReadModels.Distribution.Flat(10)
        for i in a:
            self.assert_(i == 1, "Values in Flat array are not equal to 1.")
        self.assert_(len(a) == 10, "Flat array is not the right size ")

    def testTriangle(self):
        a = ReadModels.Distribution.Triangle(50, 100, 150)
        z = 1;
        for i in a:
            self.assert_(i <= z, "Values must not rise in Triangle array")
            self.assert_(i != 0 , "Zero values should not be allowed in triangle array")
        self.assert_(len(a) == 150, "Triangle array is not the right size ")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFlat']
    unittest.main()
