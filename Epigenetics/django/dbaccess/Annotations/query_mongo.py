'''
Created on 2013-05-23

@author: sperez

'''
import Mongo_Connector
from time import time
import sys
from numpy import log, mean
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import sqrt


'''
STILL NEED TO IMPLEMENT:
    1.
        more query options
    2.
        more graph options
'''

class MongoCurious():
    '''A class to simplify plotting methylation from a mongo database'''
    def __init__(self,
                database='human_epigenetics',
                collection='methylation'):
        '''Connects to database'''
        mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database)
        self.database = database
        self.collection = collection
        self.mongo = mongo
        
    
    def query(self,
                chromosome=None,
                start = None,
                end = None,
                sample_label = None,
                exprs_value = None,
                sampletype = None,
                project = "All"):
        '''Registers query inputs'''
        if chromosome == None:
            raise ValueError("Please specificy a chromosome.")
        if isinstance(chromosome, basestring):
            self.chromosome = chromosome
        elif isinstance(chromosome, int):
            if self.collection == "methylation":
                self.chromosome = "CHR" + str(chromosome)
            if self.collection == "waves":
                self.chromosome = str(chromosome)
        self.start = start
        self.end = end
        self.sample_label = sample_label
        self.exprs_value = exprs_value
        self.project = project
        self.sampletype = sampletype
        if self.collection == "methylation":
            self.sample_groups = self.creategroups()
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
        if self.collection == "methylation":
            query_chr, query_start, query_end, query_samplabel = {}, {}, {}, {}
            if self.chromosome != None: query_chr = {"CHR":self.chromosome}
            if self.start != None: query_start =  {"start_position":{"$lte":self.end}}
            if self.end != None: query_end = {"end_position":{"$gte":self.start}}
            if self.sample_label != None: query_samplabel = {"sample_label":self.sample_label}
            query = dict(query_chr.items() + query_start.items() + query_end.items() + query_samplabel.items())
            return_chr = {'_id': False, 'beta_value': True, 
                          'start_position': True, 'end_position': True, 
                          'sample_label': True}
            probes = self.mongo.find(self.collection,query,return_chr).sort('start_position', 1)
        if self.collection == "waves":
            query_chr, query_pos, = {}, {}
            if self.chromosome != None: query_chr = {"chr":self.chromosome}
            if self.start != None and self.end != None: 
                query_pos =  {"pos":{"$lte":self.end+500, "$gte":self.start-500}} #extend the region for query to find peaks with tails in region
            query = dict(query_chr.items() + query_pos.items())
            return_chr = {'_id': False, 'pos': True, 
                          'height': True, 'stddev': True, 
                          'sample_id': True}
            probes = self.mongo.find(self.collection,query,return_chr).sort('pos', 1)
        
        if probes.count()== 0:
            print "    WARNING: The following query return zero probes!"
            print "    ---> Find(", query, ")"
            print "     use the checkquery() function to validate the inputs of your query."
            sys.exit()
            
        print "    Conducting query: Find(", query, ")"
        print "    Found %i probes." %probes.count()
        self.probes = probes
        self.count= self.probes.count()
        return self.probes
        
    
    def creategroups(self):
        '''
        Separate samples into 'groups' according to a particular feature.
        Example: feature = diseased/control.
        samplegroup is a list of sample labels with the desired sampletype
        '''
        print "    Creating sample groups..."
        if self.project == "down":
            if self.sampletype not in ["Control", "DS"]: self.sampletype = str(raw_input("Please specify a sample type: \"Control\" or \"DS\"?"))
            feature = 'Sample Group'
            samplegroup = self.sample_dict(project = self.project, feature = feature)[self.sampletype]
        if self.project == "kollman":
            if self.sampletype not in ["unstimulated", "listeria"]: self.sampletype = str(raw_input("Please specify a sample type: \"unstimulated\" or \"listeria\"?"))
            feature = 'stimulation'
            samplegroup = self.sample_dict(project = self.project, feature = feature)[self.sampletype]
        if self.project == "All":
            print "l",self.sampletype, "l"
            if self.sampletype != "control" or self.sampletype != None:
                print "The sample type \"",self.sampletype, "\" is invalid."
                self.sampletype = str(raw_input("Please specify a sample type: \"control\" or \"disease\"?"))
            if self.sampletype == "control" or self.sampletype == None:
                samplegroup  = self.sample_dict(project = "kollman", feature = "stimulation")["unstimulated"]
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group")["Control"])
                samplegroup.append(self.sample_dict(project = "kollman", feature = "stimulation", nottype = ["unstimulated", "listeria"]))
                samplegroup.append( self.sample_dict(project = "down", feature = "Sample Group", nottype = ["Control", "DS"]))
            if self.sampletype == "disease": 
                samplegroup  = self.sample_dict(project = "kollman", feature = "stimulation")["listeria"]
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group")["DS"])
        
        print "    The sample labels with sample type", self.sampletype, " are:", samplegroup
        return samplegroup
        
    def sample_dict(self, project, feature, nottype = None):
        '''
        For a particular feature (for example, if a sample is a control sample or not) return a dictionary
        tructured as {sample label: featuretype}
        '''
        print "    ", feature, project
        print "    Appending labels for project", project, "and", feature
        self.mongo.ensure_index("samples", project)    # For speed
        self.mongo.ensure_index("samples", feature)
        if nottype != None:
            add_query = {feature:{"$ne":nottype[0], "$ne":nottype[1]}}
            findQuery = dict({'project': project}.items()+add_query.items())
        else: findQuery = {'project': project}
        returnQuery = {feature: True, '_id': False, 'sample_label': True}
        
        
        samples = self.mongo.find("samples",
                             findQuery, returnQuery).sort(feature, 1)
        sample_groups = {}
        sample_labels_list = []
        previous_group = None
        count = 0
        for doc in samples:
            if (doc[feature] != previous_group) and (count > 0):
                sample_groups[previous_group] = sample_labels_list
                sample_labels_list = []
            sample_labels_list.append(doc['sample_label'])
            previous_group = doc[feature]
            count += 1
        sample_groups[previous_group] = sample_labels_list  # Do once more after exiting loop
        print sample_groups
        return sample_groups
    
    def collectbetas(self, 
                     window_size =1):
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
          
        print '    %s probes\' beta values were extracted and binned.' %count
          
        x_position = []
        y_avg = []
        for pos, tup_list in sorted(position_dic.iteritems()):
            beta_values = []
            for beta, samp in tup_list:
                if self.sampletype == None:
                    beta_values.append(beta)
                elif samp in self.sample_groups:
                    beta_values.append(beta)
                else: break
                data_avg = mean(beta_values)
                x_position.append(pos)
                y_avg.append(data_avg)            
        
        print "    %i beta values collected" %len(x_position)
        self.positions = x_position
        self.betas = y_avg
        return None
        
        
    def getwaves(self,tail = 1):
        count = 0
        #This dict will store the position as keys and height and standard deviation as values.
        waves = {}
        #"tail" is min height of a tail to be included in the plot for a peak which doesn't have its center in the region
        for doc in self.probes:
            if isinstance(doc['stddev'], basestring): int()
            pos, height, stddev = doc['pos'],doc['height'],int(doc['stddev'])
            if self.start <= pos <= self.end:
                waves[pos] = [height,stddev]
                count +=1
            else:
                dist_to_region = min(abs(pos-self.end), abs(self.start-pos))
                dist_from_peak_to_tail = sqrt((-2)*stddev*stddev*log(tail/height))
                print "        ", pos, height, stddev
                print "        tail distance", dist_from_peak_to_tail
                print "        dist to region", dist_to_region
                if dist_from_peak_to_tail-dist_to_region >=0:
                    waves[pos] = [height,stddev]
                    count +=1
                else: print "         Not included:    ", pos, height, stddev, 
        print "\n%i peaks were found in region." %count
        self.waves = waves
        print waves
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
        print "    Making svg file \"%s\"" %filename
        gene = self.makedrawing(filename=filename,color=color)
        gene.save
        return gene
    
    
    def svgtostring(self, color="blue"):
        print "Making svg string..."
        gene = self.makedrawing(color=color)
        return gene.tostring()


