'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot methylation data from the methylation collection
'''
import os, sys
from time import time
sys.path.insert(0, "/home/sperez/git/software/epigenetics-software/Epigenetics")
from MongoDB.mongoUtilities import MongoCurious

# Tell the database which collection you want to query from
t0 = time()
m = MongoCurious.MongoCurious(database = "human_epigenetics")
print " Query %.3f" % (time() - t0)

t0 = time()
query1 = m.query(collection = 'methylation', chromosome = "chr4", start = 3076407, end = 3245676)
print "Extract %.3f" % (time() - t0)

t0 = time()
m.finddocs()
print "find docs %.3f" % (time() - t0)

t0 = time()
m.collectbetas()
print "collect betas %.3f" % (time() - t0)

t0 = time()
m.svg(filename = "test_methylation.svg", title = "Huntington gene")
print "svg %.3f" % (time() - t0)
