'''Library to generate svg views of methylation data'''
import os, sys
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoEpigeneticsWrapper

def svgcode(db = None, project = None, chromosome = None, start = None,
            end = None, height = None, width = None,
            tss = False, cpg = False, datapoints = False, peaks = False):
    '''TODO:missing docstring'''
    print("Connecting to database:")
    organism = str.capitalize(db)
    database = db + "_epigenetics"
    m = MongoEpigeneticsWrapper.MongoEpigeneticsWrapper(database)
    print("Querying...")
    docs = m.query(collection = "methylation", project = project, chromosome = chromosome, start = start, end = end)
    if tss or cpg:
        m.getannotations(docs)
    if chromosome[0:3] != 'chr':
        chromosome = 'chr' + str(chromosome)
    return m.svg(to_string = True,
                 title = organism + " DNA methylation on " + chromosome + " (" + str(start) + "-" + str(end) + ")",
                 color = 'indigo',
                 height = height,
                 width = width,
                 get_tss = tss,
                 get_cpg = cpg,
                 show_points = datapoints,
                 show_peaks = peaks)

