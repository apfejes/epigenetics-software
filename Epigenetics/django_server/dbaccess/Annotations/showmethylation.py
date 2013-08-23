import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoCurious

def svgcode(db = None, chromosome = None, start = None,
            end = None, LENGTH = None, WIDTH = None, 
            MARGIN = None, tss = False, cpg = False):
    print("Connecting to database:")
    organism = str.capitalize(db)
    database = db + "_epigenetics"
    m = MongoCurious.MongoCurious(database = database)
    print("Querying...")
    docs = m.query(collection = "methylation", project = 'down syndrome', chromosome = chromosome, start = start, end = end)
    if tss or cpg:
        m.getannotations(docs)
    return m.svg(to_string = True, 
                 title = organism + " DNA methylation on chr"+str(chromosome)+" ("+str(start)+"-"+str(end) +")", 
                 color = 'indigo',
                 LENGTH = LENGTH,
                 WIDTH = WIDTH,
                 MARGIN = MARGIN,
                 get_tss = tss,
                 get_cpg = cpg)

