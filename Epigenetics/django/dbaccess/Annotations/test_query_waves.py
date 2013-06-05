'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot ChipSeq peaks from db.waves collection
'''
from query_mongo import MongoCurious

# Tell the database which collection you want to query from
m = MongoCurious(database = "human_epigenetics", collection = "waves")
# Query the database
query1 = m.query(chromosome = "chrY", start = 59001327, end = 59002433)
# Extract the probes or documents relevant to that region
m.finddocs()
# Extract the peak information in each probe
m.getwaves()
# Make the svg file called "peaks.svg" in the /SVGs folder
m.svg(filename = "test_peak.svg", color = 'indigo')


# We can now do the same with a second query using the same instance of MongoCurious
query2 = m.query(chromosome = "chr2", start = 32000, end = 38000)
m.finddocs()
m.getwaves()
m.svg(filename = "test_peak2.svg", color = 'indigo')

print query1
print query2
