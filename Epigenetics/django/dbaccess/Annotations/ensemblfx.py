'''
Created on 2013-05-14

@author: sperez

Functions for querying Ensembl.
'''
from time import time
#from cogent.db.ensembl import Genome


def get_Exons(gene):
    Exons = gene.CanonicalTranscript.Exons
    return Exons

def ExonCoordinates(Exons):
    Coordinates = []
    t0=time()
    for exon in Exons:
        coords = str(exon.Location).split(":")[3].split("-")
        coords = map(float,coords)
        Coordinates.append(coords)
    print "Query time: %.3f" % (time()-t0), "s."
    return Coordinates