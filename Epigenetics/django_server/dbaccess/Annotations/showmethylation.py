import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")

from MongoDB.mongoUtilities import MongoCurious

m = MongoCurious.MongoCurious(database = "human_epigenetics")
m.query(collection = 'methylation', chromosome = "chr4", start = 3076407, end = 3245676)
m.finddocs()
m.collectbetas()

def svgcode():
    return m.svg(title = "Huntington gene", to_string = True, length = 300.0)
