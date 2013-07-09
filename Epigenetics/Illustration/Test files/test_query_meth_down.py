'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot methylation data from the methylation collection
'''
import os, sys
from time import time
sys.path.insert(0, "/home/sperez/epigenetics-software/epigenetics-software/Epigenetics")
from MongoDB.mongoUtilities import MongoCurious

collection = 'methylation'
chromosome = 'chr21'
sampletype = "Control"
project = "down"


# Tell the database which collection you want to query from
t0 = time()
m = MongoCurious.MongoCurious(database = "human_epigenetics")
print " Query %.3f" % (time() - t0)

t0 = time()
m.query(collection = collection, chromosome = chromosome, project = project,
        sample_type = sampletype, start = 30390000, end = 30395000)
print "Extract %.3f" % (time() - t0)

t0 = time()
m.finddocs()
print "find docs %.3f" % (time() - t0)

m.collectbetas()

t0 = time()
m.svg(filename = "test_down_samples.svg", title = "Down Samples")
print "svg %.3f" % (time() - t0)


