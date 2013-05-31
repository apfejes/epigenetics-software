import query_mongo
MongoCurious = query_mongo.MongoCurious

'''
Example of how to use the class MongoCurious to plot ChipSeq peaks from db.waves collection
'''


#Tell the dtabase which collection you want to query from
m= MongoCurious(collection = "waves")
#Choose a region to query
m.query(chromosome = "chr4", start = 28800, end = 37000)
#Extract the probes or documents relevant to that region
#Note: need a better name for this function
m.finddocs()
#Extract the peak information in each probe
m.getwaves()
#Make the svg file called "peaks.svg" in the /SVGs folder
m.svg(filename = "test_peak.svg", color='indigo')
#if you want the svg file as a string:
svg_string = m.svgtostring(color="indigo")

