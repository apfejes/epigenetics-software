'''
Created on 2013-05-14

@author: sperez

largely inspired from : http://pycogent.org/examples/query_ensembl.html#query-ensembl

'''




import os
#Need to declare which release of Ensemble you want to use
Release = 67

#Check if a Ensembl Account exists, otherwise, use default Ensembl UK service
#from cogent.db.ensembl import HostAccount
#if 'ENSEMBL_ACCOUNT' in os.environ:
#    host, username, password = os.environ['ENSEMBL_ACCOUNT'].split()
#    account = HostAccount(host, username, password)
#    print "Acoount for Enseml found"
#else:
#    account = None

account = None    


from cogent.db.ensembl import Genome
human = Genome(Species='human', Release=Release, account=account)

#This variable declares you are using the Ensembl coordinates for nucleotide positions
#Note that Python coordinates begin at 0 and Ensembl coords begin at 1.
ensembl_coord=True

from time import time
#Here is an example of a query using an ensembl id for Huntington's gene
t0 = time()
htt = human.getGeneByStableId(StableId='ENSG00000197386')
print htt.Description
print htt.Location
print time()-t0
#Similarly, you could have done your search using:


#Here is where the annotation features come in handy:
t0 = time()
annot_brca1 = brca1.getAnnotatedSeq(feature_types='gene')
duration = time() - t0
print duration, annot_brca1.getAnnotationsMatching

#Getting coding regions
t0 = time()
cds = annot_brca1.getAnnotationsMatching('CDS')
print time()-t0, cds, cds.getCoordinates()



