'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot ChipSeq peaks from db.waves collection
'''
import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)

sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import MongoCurious

# Tell the database which collection you want to query from
m = MongoCurious.MongoCurious(database = "human_epigenetics")
# Query the database

query1 = m.query(collection = "waves", chromosome = "chrY", start = 59001000, end = 59012000)
# Extract the probes or documents relevant to that region
m.finddocs()
# Extract the peak information in each probe
m.getwaves()
# Make the svg file called "peaks.svg" in the /SVGs folder
m.svg(filename = "test_peak.svg", color = 'indigo')


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

