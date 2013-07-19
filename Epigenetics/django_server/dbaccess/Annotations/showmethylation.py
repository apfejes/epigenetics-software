import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoCurious

print("Connecting to database:")
m = MongoCurious.MongoCurious(database = "human_epigenetics")

#For Huntington gene
#chromosome = 'chr4', start = 3076407, end = 3245676)

def svgcode(chr = None, start = None, end = None):
    print("Querying...")
    query1 = m.query(collection = "methylation", chromosome = chr, start = start, end = end)
    m.finddocs()
    m.collectbetas()
    return m.svg(to_string = True, title = "Methylation data on chr "+str(chr)+" ("+str(start)+"-"+str(end) +")", color = 'indigo', length = 300.0)

