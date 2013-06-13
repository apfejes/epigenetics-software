'''
Created on 2013-05-14

@author: sperez

largely inspired from : http://pycogent.org/examples/query_ensembl.html#query-ensembl
and: http://pycogent.org/cookbook/accessing_databases.html

'''

from cogent.db.ensembl.genome import Genome
# import the functions
import django_server.dbaccess.Annotations.ensemblfx as fx

# Need to declare which release of Ensemble you want to use adn the account
Release, account = 67, None
human = Genome(Species = 'human', Release = Release, account = account)
ensembl_coord = True

# We want the coordinates of the exons of the Huntington gene

GeneId = 'ENSG00000197386'
# First we grab the gene from Ensembl
gene = human.getGeneByStableId(StableId = GeneId)
name = gene.Description.split(" ")[0].capitalize()
l = str(gene.Location).split(":")
location = "Chr " + l[2] + ": " + l[3]

# Then we get the Exons
exons = fx.get_Exons(gene)

# We get the coordinates as a list of [Start, End] pairs.
coordinates = fx.ExonCoordinates(exons)
exon_lengths = [pair[1] - pair[0] for pair in coordinates]
