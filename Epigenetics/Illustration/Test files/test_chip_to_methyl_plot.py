'''
Created on 2013-06-07

@author: sperez

There are two ways to combine data in 1 plot. Either we query the chipseq data first (executed when chip_first = True)
and then query the methylation data. Or we can do the opposite.
'''
import os, sys
from time import time
sys.path.insert(0, "/home/sperez/epigenetics-software/epigenetics-software/Epigenetics")
from MongoDB.mongoUtilities import MongoCurious


m = MongoCurious.MongoCurious(database = "human_epigenetics")

collection = 'methylation'
chromosome = 'chr11'
project = "down"
gene='SLC22A18AS'
start = 2909327
end = 2925175

chip_first = False


if chip_first:
    # Collect waves data
    query_waves = m.query(collection = "waves", chromosome = chromosome, start = start, end = end)
    m.finddocs()
    m.getwaves()
    # Store elements of the svg peaks in a list called waves
    waves = m.svg(title = "Huntington gene", get_elements = True)

    # Collecting the methylation data
    query_betas = m.query(collection = "methylation", project = project, chromosome = chromosome, start = start, end = end)
    m.finddocs()
    m.collectbetas()
    drawing = m.svg(filename = "test_doubleplot.svg", title = gene)
    # Adding the waves to the metylation drawing
    drawing.add_data(elements = waves)
    # Saving the combined plot
    drawing.save()

else:
    # Collect methylation data
    query_betas = m.query(collection = "methylation", project = project, chromosome = chromosome, start = start, end = end)
    # Store elements of the svg methylation points in a list called points
    points = m.svg(get_elements = True)
    # Collecting the methylation data
    query_waves = m.query(collection = "waves", chromosome = chromosome, start = start, end = end)
    m.finddocs()
    m.getwaves()
    drawing = m.svg(filename = "test_doubleplot2.svg", title = gene)
    # Adding the waves to the metylation drawing
    drawing.add_data(elements = points)
    # Saving the combined plot
    drawing.save()

