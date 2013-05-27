'''
Created on 2013-05-23

@author: sperez

'''
import Mongo_Connector
from time import time
import sys
import numpy as np
from svgwrite.drawing import Drawing
from svgwrite.path import Path


'''
STILL NEED TO IMPLEMENT:
    1.
        more query options
    2.
        more graph options
    3.
        sample type option
'''

class MongoCurious():
    '''A class to simplify plotting methylation from a mongo database'''
    def __init__(self,
                database='human_epigenetics',
                collection='methylation'):
        '''Connects to database and puts index on the collection'''
        mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database)
        self.database = database
        self.collection = collection
        self.mongo = mongo
    
    
    def query(self,
                chromosome=None,
                start = None,
                end = None,
                sampletype = None,
                project = None):
        '''Registers query inputs'''
        if chromosome == None:
            raise ValueError("Please specificy a chromosome.")
        self.chromosome = chromosome
        self.start = start
        self.end = end
        self.sampletype = sampletype
        self.project = project
        return self
    
    
    def checkquery(self):
        '''Checks that query inputs are valid'''
        t0 = time()
        self.mongo.ensure_index(self.collection, 'CHR')
        print "Checking validity of query inputs..."
        if self.chromosome != None:
            Chromosomes = self.mongo.distinct(self.collection, "CHR")
            if self.chromosome not in Chromosomes:
                raise ValueError("Invalid chromosome name. Please choose from the following possible inputs:", Chromosomes.encode("utf-8"))
            
        if self.project != None:
            Projects = self.mongo.distinct(self.collection, "project")
            if self.project not in Projects:
                raise ValueError("Invalid project. Please choose from the following:", Projects)
        print "Input check done in %i seconds." %round(time()-t0,1)
        return None
        
        
    def findprobes(self):
        '''Finds probes corresponding to query'''
        self.mongo.ensure_index(self.collection, 'start_position') #for speed? to be tested...
        
        #Preparing the different features of the query
        if self.chromosome != None:
            query_chr = {"CHR":self.chromosome}
        else: query_chr = {}
        
        if self.start != None:
            query_start =  {"start_position":{"$lte":self.end}}
        else: query_start = {}
        
        if self.end != None:
            query_end = {"end_position":{"$gte":self.start}}
        else: query_end = {}
        
        query = dict(query_chr.items() + query_start.items() + query_end.items())
            
        return_chr = {'_id': False, 'beta_value': True, 
                      'start_position': True, 'end_position': True, 
                      'sample_label': True}
                      
        probes = self.mongo.find(self.collection,query,return_chr).sort('start_position', 1)
        
        if probes.count()== 0:
            print "WARNING: The following query return zero probes!"
            print "---> Find(", query, ")"
            print " use the checkquery() function to validate the inputs of your query."
            sys.exit()
            
        print "Conducting query: Find(", query, ")"
        print "Found %i probes." %probes.count()
        self.probes = probes
        self.count= self.probes.count()
        return self.probes
        
    
    def createsamplegroups(self, project, sampletype):
        '''
        Separate samples into 'groups' according to a particular feature.
        Example: feature = diseased/control, sex, tissue type...
        
        Returns a dictionary of key:value pairs where key is the name of the 
        feature (e.g. diseased/control) and value is a list of sample labels
        that are in that feature group. 
        '''
        sample_collection = 'samples'
        self.mongo.ensure_index(sample_collection, project)    # For speed
        self.mongo.ensure_index(sample_collection, sampletype)
        
        findQuery = {'project': project}
        returnQuery = {sampletype: True, '_id': False, 'sample_label': True}
        
        
        samples = self.mongo.find(sample_collection, 
                            findQuery, returnQuery).sort(sampletype, 1)
        sample_groups = {}
        sample_labels_list = []
        previous_group = None
        count = 0
        for doc in samples:
            '''
            For each doc, keep track of previous group feature (e.g. whether
            previous doc was diseased or control). Since it is ordered by 
            the feature, it will go through all of samples of one feature 
            before moving on to the other. We use this as an indicator that
            all samples in that group have been iterated.
            
            We keep extending a list, sample_label_list, to add sample_labels
            for all the samples within one group. 
            
            When all samples in that group have been iterated (the if statement),
            then we create a key:value pair in the dictionary, sample_groups, where
            key is the feature (e.g. diseased or control) and value is sample_label_list.
            
            Empty sample_label_list and keep doing this for all feature groups. 
            '''
            if (doc[sampletype] != previous_group) and (count > 0):
                sample_groups[previous_group] = sample_labels_list
                sample_labels_list = []
            sample_labels_list.append(doc['sample_label'])
            previous_group = doc[sampletype]
            count += 1
        sample_groups[previous_group] = sample_labels_list  # Do once more after exiting loop
        return sample_groups
    
    
    def collectbetas(self, 
                     window_size =1, 
                     sample_type = None):
        '''Collects and bins methylation data'''
        
        #Bin the beta values and collect average positions
        position_dic = {}
        betasamp_list = []
        count = 0
        for doc in self.probes:
            if count == 0:
                prev_start_pos = doc['start_position']
            if count != 0:
                if (doc['start_position'] - prev_start_pos) > window_size:
                    avg_position = (doc['start_position'] + prev_start_pos) / 2
                    position_dic[avg_position] = betasamp_list
                    betasamp_list = []
                    prev_start_pos = doc['start_position']
            betasamp_list.append((doc['beta_value'], doc['sample_label']))
            count += 1
        avg_position = (doc['start_position'] + prev_start_pos) / 2
        position_dic[avg_position] = betasamp_list
          
        print '%s probes\' beta values were extracted and binned.' %count
          
        x_position = []
        y_avg = []
        for pos, tup_list in sorted(position_dic.iteritems()):
            beta_values = []
            for beta, samp in tup_list:
                if sample_type == None or samp == sample_type:
                    beta_values.append(beta)
                data_avg = np.mean(beta_values)
                x_position.append(pos)
                y_avg.append(data_avg)            
        
        self.positions = x_position
        self.betas = y_avg
        return None
        
        
    def makedrawing(self, 
                    filename="plot.svg", 
                    color = "blue"):
        '''Make svg drawing. This function is not to b called directly, only by svg() and svgtostring() '''
        X,Y=self.positions, self.betas
        
        smooth = False
        offset =  X[0]
        invertby = max(Y)

        X = [round(float(item-offset)/20000,3)+20 for item in X]
        Y = [round((invertby-item)*1000,2)+20 for item in Y]
        
        #d is the list of coordinates with commands such as
        #M for "move to' to initiate curve and S for smooth curve
        d = "M"+str(X[0])+","+str(Y[0])+" "+str(X[1])+","+str(Y[1])
        if smooth: d = d +"S"
        for i in range(2,len(X)):
            d=d+(" "+str(X[i])+","+str(Y[i]))
            
        length, height = str(X[-1]), str(max(Y))
        
        gene = Drawing("SVGs/"+filename, size=(str(float(length)+10) + "mm", str(float(height)+10)+ "mm"), viewBox=("0 0 "+str(float(length)+10)+" "+str(float(height)+10)), preserveAspectRatio="xMinYMin meet")
        gene.add(Path(stroke = color, fill = "none", d = d))
        return gene
        
        
    def svg(self, filename = "plot.svg", color="blue"):
        print "Making svg file \"%s\"" %filename
        gene = self.makedrawing(filename=filename,color=color)
        gene.save
        return gene
    
    
    def svgtostring(self, color="blue"):
        print "Making svg string..."
        gene = self.makedrawing(color=color)
        return gene.tostring()




#Example of how to use the class
methylation= MongoCurious()
endgene = 3245676
startgene =  3076407
methylation.query(chromosome = "chr3", start = startgene, end = endgene, project = "down")
methylation.findprobes()
methylation.collectbetas()
svg = methylation.svg(filename = "test.svg", color = "green")
svg.save()