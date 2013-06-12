'''
Created on 2013-05-30

@author: sperez

Example of how to use the class MongoCurious to plot methylation data from the methylation collection
'''
import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)

sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import MongoCurious

# Tell the database which collection you want to query from
m = MongoCurious.MongoCurious(database = "human_epigenetics")
# Query the database

query1 = m.query(collection = 'methylation', chromosome = "chr4", start = 3076407, end = 3245676)
# Extract the probes or documents relevant to that region
m.finddocs()
# Extract the peak information in each probe
m.collectbetas()
# Make the svg file called "peaks.svg" in the /SVGs folder
drawing = m.svg(filename = "test_methylation.svg", title = "Huntington gene")
print len(drawing.get_items())
