from query_mongo import MongoCurious


'''
Example of how to use the class MongoCurious to plot ChipSeq peaks from db.waves collection
'''


#Tell the database which collection you want to query from
MC = MongoCurious(database ="human_epigenetics", collection = "waves")

query1 = MC.query(chromosome = "chr4", start = 28800, end = 37000)
print query1
MC.finddocs()
MC.getwaves()
query2 = MC.query(chromosome = "chr2", start = 1000, end = 40000)
print query2
MC.finddocs()
MC.getwaves()
print query1
print query2
#MC.svg(filename = "test_peak.svg", color='indigo')


'''
#Choose a region to query
query = M.query(chromosome = "chr4", start = 28800, end = 37000)
print query
#Extract the probes or documents relevant to that region
#Note: need a better name for this function
query['documents']= M.finddocs()
#Extract the peak information in each probe
m.getwaves()
#Make the svg file called "peaks.svg" in the /SVGs folder
m.svg(filename = "test_peak.svg", color='indigo')
#if you want the svg file as a string:
svg_string = m.svgtostring(color="indigo")
'''