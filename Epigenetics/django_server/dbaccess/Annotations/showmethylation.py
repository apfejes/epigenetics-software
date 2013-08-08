import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoCurious


#For Huntington gene
#chromosome = 'chr4', start = 3076407, end = 3245676)

def svgcode(db = None, chromosome = None, start = None, end = None):
    print("Connecting to database:")
    organism = str.capitalize(db)
    database = db + "_epigenetics"
    m = MongoCurious.MongoCurious(database = database)
    print("Querying...")
    message = m.query(collection = "methylation", chromosome = chromosome, start = start, end = end)
    print message
    #if message:
    #    return message
    return m.svg(to_string = True, title = organism + "DNA methylation data on  "+str(chromosome)+" ("+str(start)+"-"+str(end) +")", color = 'indigo', length = 300.0)

