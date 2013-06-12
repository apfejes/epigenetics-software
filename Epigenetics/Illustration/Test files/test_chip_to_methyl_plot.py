import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)

sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import MongoCurious


m = MongoCurious.MongoCurious(database = "human_epigenetics")

# Collect waves data
query_waves = m.query(collection = "waves", chromosome = "chr4", start = 3076407, end = 3100000)
m.finddocs()
m.getwaves()
# Store elements of the svg peaks in a list called waves
waves = m.svg(title = "Huntington gene", get_elements = True)

# Collecting the methylation data
query_betas = m.query(collection = "methylation", chromosome = "chr4", start = 3076407, end = 3100000)
m.finddocs()
m.collectbetas()
drawing = m.svg(filename = "test_doubleplot.svg", title = "Huntington gene")
# Adding the waves to the metylation drawing
drawing.add_data(elements = waves)
# Saving the combined plot
drawing.save()
