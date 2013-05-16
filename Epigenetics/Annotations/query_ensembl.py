'''
Created on 2013-05-14

@author: sperez

largely inspired from : http://pycogent.org/examples/query_ensembl.html#query-ensembl
and: http://pycogent.org/cookbook/accessing_databases.html

'''

from cogent.db.ensembl.genome import Genome
#import the functions 
from ensemblfx import get_Exons, ExonCoordinates

#Need to declare which release of Ensemble you want to use adn the account
Release, account = 67, None
human = Genome(Species='human', Release=Release, account=account)
ensembl_coord=True

#We want the coordinates of the exons of the Huntington gene
Huntingtons = 'ENSG00000197386'
GeneId = Huntingtons

#First we grab the gene from Ensembl
gene = human.getGeneByStableId(StableId=GeneId)

#Then we get the Exons
exons = get_Exons(gene)

#We get the coordinates as a list of [Start, End] pairs.
coordinates = ExonCoordinates(exons)
exon_lengths = [pair[1]-pair[0] for pair in coordinates]