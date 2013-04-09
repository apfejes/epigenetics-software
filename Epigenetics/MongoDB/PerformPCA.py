'''
Created on 2013-04-05

@author: jyeung
'''

# Import Python packages
from mongoUtilities import ConnectToMongo, GetMongoCursor, CreateArrayFromCursor, PlotPCA
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from matplotlib.mlab import PCA
import numpy as np


# Import R packages
base = importr('base')
stats = importr('stats')
grdevices = importr('grDevices')
graphics = importr('graphics')


# Connect to database
dbname = 'epigenetics_database'
db = ConnectToMongo.ConnectToMongo(dbname)

# Get a collection
collname = "down_kwargs"
collection = db[collname]

# Ensure an index for beta values.
collection.ensure_index("beta_value")
collection.ensure_index("sample_name")

# Get probe_list and retrieve data (betas) from collection
data_collection = GetMongoCursor.Cursor(collection)
design_info = data_collection.GetDocsWithKeys('SampleLabel')
number_of_samples = design_info.count()
beta_cursor = data_collection.GetDocsWithKeys('beta_value').sort("sample_name", 1)
betas_per_sample = beta_cursor.count()/number_of_samples
array_betas = CreateArrayFromCursor.CreateArrayFromCursor(beta_cursor, 
                                                          number_of_samples, 
                                                          betas_per_sample,
                                                          'beta_value')
PCA_results = PCA(array_betas)
PlotPCA.PlotPCA3D(PCA_results)
print('done')

'''
beta_list = []
for doc_beta in beta_cursor:
    beta_list.append(doc_beta['beta_value'])
array_betas = np.array(beta_list)
array_betas = array_betas.reshape(number_of_samples, betas_per_sample)
array_betas = array_betas.transpose()
print array_betas
'''




'''
beta_cursor.rewind()
count = 0
for i in xrange(1, 6):
    print beta_cursor[count]
    count = count + 1
'''
'''
list_beta = []
for doc_beta in betas_per_sample:
    list_beta.append(doc_beta['beta_value'])
beta_array = np.array(list_beta)
beta_array.shape()
beta_array = np.fromiter(betas_per_sample, np.float)
print beta_array
'''


'''
# Create vector of betas
beta_list = []
sample_list = []
for doc in beta_cursor:
    beta_list.append(doc['beta_value'])
    sample_list.append(doc['sample_name'])
    
# Create vector of sample names
samp_names = []
for des_doc in design_info:
    samp_names.append(des_doc['SampleLabel'])
print samp_names
print beta_list[0:5]
print sample_list[0:5]


# Create matrix
# m = base.matrix(doc_list, nrow=betas_per_sample, ncol=number_of_samples)
# m = robjects.r['matrix'](doc_list, nrow=betas_per_sample, ncol=number_of_samples)
# Must input r.matrix as FloatVector and not list to get PCA to work...
m = robjects.r.matrix(robjects.FloatVector(beta_list), 
                      nrow=betas_per_sample, 
                      ncol=number_of_samples)
print m

'''
'''
beta_cursor.clone()
count = 0
for i in xrange(1, 6):
    print beta_cursor[count].get('beta_value')
    count = count + 1
'''


'''
# Fill matrix with beta values. 
pca = stats.prcomp(m)
colors = robjects.StrVector(['blue', 'black'])    # For plotting
color_vector = base.rep(colors, each=robjects.Vector(betas_per_sample))
grdevices.pdf("/home/jyeung/Documents/rpy2_graphics/PCA_down.pdf")
graphics.plot(pca, main="Eigen values")
stats.biplot(pca, main="biplot", col=color_vector)
grdevices.dev_off()
'''



