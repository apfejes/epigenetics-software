'''
Created on 2013-03-28

@author: jyeung
'''


# from mongoUtilities import FilesInDirectory
from MongoDB.mongoUtilities import ConnectToMongo, GetMongoCursor, MongoDocs, PlotBarGraph
import pylab


# Connect to database
db = ConnectToMongo.ConnectToMongo()

# Get a collection
collname = "down_kwargs"
collection = db[collname]


# Get probe_list and retrieve data (betas) from collection
data_collection = GetMongoCursor.Cursor(collection)

# Retrieve list of probes in chromosome 21. 
probes = data_collection.GetProbesInChromosome(21)
probe_list = probes.keys()
docs_betas = data_collection.GetBetasFromProbes(probe_list)   # Improve this function

# Retrieve design information
design_info = data_collection.GetDocsWithKeys('SampleLabel')    # Create cursor
design_docs = MongoDocs.Cursor(design_info)    # Create object to play with cursor
groups = set(design_docs.GetValuesFromKey('Sample Group'))

# Modularize this...

samples_by_groups = {}    # Initialize
for group in groups:
    list_samples = []    # Initialize
    for doc in design_docs.cursor.clone():
        if group in doc.values():
            list_samples.append(doc['SampleID'])
    samples_by_groups[group] = list_samples
print(samples_by_groups)

betas_sample = {}    # Initialize
for group, samples in samples_by_groups.iteritems():
    for samp in samples:
        list_betas = []    # Initialize
        list_avg = []
        docs_betas = docs_betas.clone()
        for doc in docs_betas:
            if samp in doc.values():
                list_betas.append(doc['beta_value'])
        list_avg = sum(list_betas) / len(list_betas)
        betas_sample[samp] = list_avg
print betas_sample

PlotBarGraph.PlotBarGraph(betas_sample, 'Avg Betas Across Samples in Chromosome 21')


        

                
                
                 
        
        


    
    

        



    
'''
samples = design_docs.GetValuesFromKey('SampleID')
for s in samples:
    print s
'''
    
'''
for group in groups:
    for doc in design_docs.documents:
        print doc
        sample_list = []    # Initialize
        sample_list = []
        sample_dict['group'] = []
'''
    
    

chromosome_unique = []
# chromosome_unique.append(x for x in range(1, 22))
# print(chromosome_unique)

'''
for x in range(1, 22):
    chromosome_unique.append(str(x))
chromosome_unique.append('X')
chromosome_unique.append('Y')
print(chromosome_unique)
'''


# Find all documents in fData, show only probename and chromosome
# fData = collection.find({'MAPINFO': {'$exists': True}}, {'MAPINFO': 1, 'NAME': 1})

'''
fData = collection.find({'MAPINFO': {'$exists': True}}, {'MAPINFO': 1, 'NAME': 1})
chromosomes = []
for dat in fData:
    chromosomes.append(dat['MAPINFO'])
chromosome_unique = set(chromosomes)
print(chromosome_unique)
'''