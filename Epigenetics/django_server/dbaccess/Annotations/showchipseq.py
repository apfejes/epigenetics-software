import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoCurious

m = MongoCurious.MongoCurious(database = "human_epigenetics")


query1 = m.query(collection = "waves", chromosome = "chr4", start = 3076407, end = 3245676)
m.finddocs()
m.getwaves()

def svgcode():
    return m.svg(to_string = True, title = "Huntington gene", color = 'indigo')
