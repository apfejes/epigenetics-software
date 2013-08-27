'''
Created on 2013-05-14

@author: sperez

Functions for querying Ensembl.
'''
from time import time
import gc
# from cogent.db.ensembl import Genome


def get_Exons(gene):
    ''' TODO: fill in docstring '''
    Exons = gene.CanonicalTranscript.Exons
    return Exons

def ExonCoordinates(Exons):
    ''' TODO: fill in docstring '''
    Coordinates = []
    gc.disable()
    t0 = time()
    for exon in Exons:
        coords = str(exon.Location).split(":")[3].split("-")
        coords = map(float, coords)
        Coordinates.append(coords)
    gc.enable()
    print "Query time: %.3f" % (time() - t0), "s."
    return Coordinates
