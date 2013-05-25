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
        endgene = 3245676
        startgene =  3076407
        query = {"CHR":"chr4","project":"kollman","start_position":{"$lte":endgene},"end_position":{"$gte":startgene}}
    2.
        more query options
    3.
        more graph options
    4.
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
                end = None):
        '''Registers query inputs'''
        if chromosome == None:
            raise ValueError("Please specificy a chromosome.")
        self.chromosome = chromosome
        self.start = start
        self.end = end
        return self
    
    
    def checkquery(self):
        '''Checks that query inputs are valid'''
        t0 = time()
        self.mongo.ensure_index(self.collection, 'CHR')
        
        Chromosomes = self.mongo.distinct(self.collection, "CHR")
        if self.chromosome not in Chromosomes:
            raise ValueError("Invalid chromosome name. Please choose from the following possible inputs:", Chromosomes.encode("utf-8"))
            
        if self.start != None:
            Starts = self.mongo.distinct(self.collection, "start_position")
            if self.start not in [min(Starts),max(Starts)]:
                raise ValueError("Invalid starting position. Please choose between:", min(Starts),"and", max(Starts))
        
        if self.end != None:
            Ends = self.mongo.distinct(self.collection, "end_position")
            if self.end not in [min(Ends),max(Ends)]:
                raise ValueError("Invalid ending position. Please choose between:", min(Ends),"and", max(Ends))

        print "Input check done in %i seconds." %round(time()-t0,1)
        return None
        
        
    def findprobes(self):
        '''Finds probes corresponding to query'''
        self.mongo.ensure_index(self.collection, 'start_position') #for speed? to be tested...
        
        if self.start == None and self.end == None:
            query = {"CHR":self.chromosome}
        elif self.start == None: 
            query = {"CHR":self.chromosome, "end_position":{"$gte":self.start}}
        elif self.end == None: 
            query = {"CHR":self.chromosome, "start_position":{"$lte":self.end}}
        else: 
            query = {"CHR":self.chromosome, "start_position":{"$lte":self.end}, "end_position":{"$gte":self.start}}
            
        return_chr = {'_id': False, 'beta_value': True, 
                      'start_position': True, 'end_position': True, 
                      'sample_label': True}
                      
        probes = self.mongo.find(self.collection,query,return_chr).sort('start_position', 1)
        
        if probes.count()== 0:
            print "WARNING: The following query return zero probes!"
            print "---> Find(", query, ")"
            print "Exiting..."
            sys.exit()
            
        print "Conducting query: Find(", query, ")"
        print "Found %i probes." %probes.count()
        self.probes = probes
        self.count= self.probes.count()
        return self.probes
        
        
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
        return None
    
    
    def svgtostring(self, color="blue"):
        print "Making svg string..."
        gene = self.makedrawing(color=color)
        return gene.tostring()




#Example of how to use the class
methylation= MongoCurious()
print methylation.database, methylation.collection
methylation.query(chromosome = "chr3")
methylation.findprobes()
methylation.count
methylation.collectbetas()
string = methylation.svgtostring()
print string