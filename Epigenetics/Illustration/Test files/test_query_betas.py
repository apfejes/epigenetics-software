'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot methylation data from the methylation collection
'''
import os, sys
from time import time
sys.path.insert(0, "/home/sperez/epigenetics-software/epigenetics-software/Epigenetics")
from MongoDB.mongoUtilities import MongoCurious

database = "human_epigenetics"
# Tell the database which collection you want to query from
t0 = time()
m = MongoCurious.MongoCurious(database = database)
print " Query %.3f" % (time() - t0)

#for htt
chr = 'chr4'
start = 3076408 
end = 3245687

t0 = time()
query = m.query(collection = 'methylation', project = 'down', chromosome = chr, start = start, end = end)
print "Extract %.3f" % (time() - t0)

t0 = time()
m.collectbetas()
print "collect betas %.3f" % (time() - t0)

t0 = time()
m.svg(filename = "test_gaussian_meth.svg", title = "Huntington gene")
print "svg %.3f" % (time() - t0)
