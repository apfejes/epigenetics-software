'''
Created on 2013-04-09

@author: jyeung
'''


from mongoUtilities import ConnectToMongo, FilesInDirectory
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


# Install packages
install = robjects.r(
'''
# source("http://bioconductor.org/biocLite.R")
# biocLite("AnnotationForge")
# source("http://bioconductor.org/biocLite.R")
# biocLite("IlluminaHumanMethylation450k.db")
''')

methylation_annotation = importr('IlluminaHumanMethylation450k.db')

mapped_probes = robjects.r['mappedkeys']
probe_chr_loc = mapped_probes('IlluminaHumanMethylation450kCHRLoc')
print probe_chr_loc





'''
# Connect to 'annotation' database
db = ConnectToMongo.ConnectToMongo('annotation')

# Set directory, grab all filenames in that directory.
InputDir = '/home/jyeung/Documents/Outputs/Down'
files = FilesInDirectory.Files(InputDir)

# Create a collection for inserting documents
# collection_name = raw_input('Insert collection name for inserting documents: ')
collection_name = 'methylation2'
collection = db[collection_name]

with open('{0}{1}{2}'.format(files.directory, "/", files.annotation_fnames[0]), 'rb') as Data:
    reader = csv.reader(Data, delimiter='\t')
    rownames = reader.next()
    print rownames
    for row in reader:
        data_row = row
        print data_row
        break
with open('{0}{1}{2}'.format(files.directory, "/", files.annotation_fnames[0]), 'rb') as Data:
    reader = csv.DictReader(Data, delimiter = '\t')
    dictRow = reader.next()
    print dictRow
print len(rownames)
print len(data_row)
print len(dictRow)
'''

'''
    readerDic = csv.DictReader(Data, delimiter = '\t')
    for row in readerDic:
        print row
        break
'''


'''
# 4.
files.InsertRowsToDB(files.annotation_fnames, collection,
                     filetype = 'annotation')
'''




