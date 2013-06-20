'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot ChipSeq peaks from db.waves collection
'''
import os, sys
from time import time
sys.path.insert(0, "/home/sperez/epigenetics-software/epigenetics-software/Epigenetics")
from MongoDB.mongoUtilities import MongoCurious
t0 = time()
# Tell the database which collection you want to query from
m = MongoCurious.MongoCurious(database = "human_epigenetics")
# Query the database

query1 = m.query(collection = "waves", chromosome = "chr4", start = 3076407, end = 3245676)
# Extract the probes or documents relevant to that region
m.finddocs()
# Extract the peak information in each probe
m.getwaves()
# Make the svg file called "peaks.svg" in the /SVGs folder
m.svg(filename = "test_peak.svg", title = "Huntington gene", color = 'indigo')

print time() - t0
#
# query1 = m.query(chromosome = "chrY", start = 59001100, end = 59002000)
# # Extract the probes or documents relevant to that region
# m.finddocs()
# # Extract the peak information in each probe
# m.getwaves()
# # Make the svg file called "peaks.svg" in the /SVGs folder
# m.svg(filename = "test_peak2.svg", color = 'indigo')
#
# query1 = m.query(chromosome = "chrY", start = 59001000, end = 59009000)
# # Extract the probes or documents relevant to that region
# m.finddocs()
# # Extract the peak information in each probe
# m.getwaves()
# # Make the svg file called "peaks.svg" in the /SVGs folder
# m.svg(filename = "test_peak3.svg", color = 'indigo')

# We can now do the same with a second query using the same instance of MongoCurious
# query2 = m.query(chromosome = "chr2", start = 32000, end = 38000)
# m.finddocs()
# m.getwaves()
# m.svg(filename = "test_peak2.svg", color='indigo')
#
# print query1
# print query2

