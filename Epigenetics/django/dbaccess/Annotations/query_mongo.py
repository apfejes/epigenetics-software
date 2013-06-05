'''
Created on 2013-05-23

@author: sperez

'''
import Mongo_Connector
from time import time
import sys
from numpy import log, mean
from svgwrite.drawing import Drawing
from svgwrite.text import Text
from svgwrite.shapes import Rect
from svgwrite.path import Path
from math import sqrt, exp
from query_class import MongoQuery

'''
STILL NEED TO IMPLEMENT:
    1.
        more query options
    2.
        more graph options
'''

class MongoCurious():
    '''A class to simplify plotting methylation and chipseq data from a mongo database'''
    def __init__(self,
                database = None,
                collection = None):
        '''Connects to database'''
        if database == None:
            raise ValueError("Please specify a database.")
        self.mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database)
        if collection == None:
            raise ValueError("Please specify a collection.")
        self.database = database
        self.collection = collection

    def query(self,
                chromosome = None,
                start = None,
                end = None,
                sample_label = None,
                exprs_value = None,
                sample_type = None,
                project = "All"):
        '''Stores query inputs and parameters as an instance of MongoQuery'''
        Query = MongoQuery()
        Query['database'] = self.database
        Query['collection'] = self.collection
        if chromosome == None:
            raise ValueError("Please specificy a chromosome.")
        if isinstance(chromosome, basestring):
            Query['chromosome'] = chromosome
            self.chromosome = chromosome
        elif isinstance(chromosome, int):
                Query['chromosome'] = "chr" + str(chromosome)
                self.chromosome = chromosome
        Query['start'] = start
        self.start = start
        Query['end'] = end
        self.end = end
        Query['sample label'] = sample_label
        self.sample_label = sample_label
        Query['project'] = project
        self.project = project
        Query['sample type'] = sample_type
        self.sample_type = sample_type
        if self.project:
            self.sample_groups = self.creategroups()
            Query['sample groups'] = self.sample._groups
        self.Query = Query
        return self.Query

    def checkquery(self):
        '''Checks that query inputs are valid'''
        t0 = time()
        self.mongo.ensure_index(self.collection, 'CHR')
        print "Checking validity of query inputs..."
        if self.chromosome != None:
            Chromosomes = self.mongo.distinct(self.collection, "CHR")
            if self.chromosome not in Chromosomes:
                raise ValueError("Invalid chromosome name. Please choose from the following possible inputs:",
                                 Chromosomes.encode("utf-8"))

        if self.project != None:
            Projects = self.mongo.distinct(self.collection, "project")
            if self.project not in Projects:
                raise ValueError("Invalid project. Please choose from the following:", Projects)
        print "Input check done in %i seconds." % round(time() - t0, 1)
        return None


    def finddocs(self):
        '''Finds probes or documents corresponding to query'''
        self.mongo.ensure_index(self.collection, 'start_position')    # for speed? to be tested...

        # Preparing the different features of the query
        if self.collection == "methylation":
            query_chr, query_start, query_end, query_samplabel = {}, {}, {}, {}
            if self.chromosome != None: query_chr = {"CHR":self.chromosome}
            if self.start != None: query_start = {"start_position":{"$lte":self.end}}
            if self.end != None: query_end = {"end_position":{"$gte":self.start}}
            if self.sample_label != None: query_samplabel = {"sample_label":self.sample_label}
            query = dict(query_chr.items() + query_start.items() + query_end.items() + query_samplabel.items())
            return_chr = {'_id': False, 'beta_value': True,
                          'start_position': True, 'end_position': True,
                          'sample_label': True}
            docs = self.mongo.find(self.collection, query, return_chr).sort('start_position', 1)
        if self.collection == "waves":
            query_chr, query_pos, = {}, {}
            if self.chromosome != None: query_chr = {"chr":self.chromosome}
            if self.start != None and self.end != None:
                query_pos = {"pos":{"$lte":self.end + 500, "$gte":self.start - 500}}    # extend the region of query
            query = dict(query_chr.items() + query_pos.items())
            return_chr = {'_id': False, 'pos': True,
                          'height': True, 'stddev': True,
                          'sample_id': True}
            docs = self.mongo.find(self.collection, query, return_chr).sort('pos', 1)

        if docs.count() == 0:
            print "    WARNING: The following query return zero probes or documents!"
            print "    ---> Find(", query, ")"
            print "     use the checkquery() function to validate the inputs of your query."
            sys.exit()

        print "\n Conducting query: Find(", query, ")"
        print " Found %i probes or documents." % docs.count()
        self.docs = docs
        self.count = self.docs.count()
        self.Query['cursor'] = self.docs
        return None


    def creategroups(self):
        '''
        Separate samples into 'groups' according to a particular feature.
        Example: feature = diseased/control.
        samplegroup is a list of sample labels with the desired sample_type
        '''
        print "    Creating sample groups..."
        if self.project == "down":
            if self.sample_type not in ["Control", "DS"]: self.sample_type = str(raw_input(
            				"Please specify a sample type: \"Control\" or \"DS\"?"))
            feature = 'Sample Group'
            samplegroup = self.sample_dict(project = self.project, feature = feature)[self.sample_type]
        if self.project == "kollman":
            if self.sample_type not in ["unstimulated", "listeria"]: self.sample_type = str(raw_input(
            				"Please specify a sample type: \"unstimulated\" or \"listeria\"?"))
            feature = 'stimulation'
            samplegroup = self.sample_dict(project = self.project, feature = feature)[self.sample_type]
        if self.project == "All":
            print "l", self.sample_type, "l"
            if self.sample_type != "control" or self.sample_type != None:
                print "The sample type \"", self.sample_type, "\" is invalid."
                self.sample_type = str(raw_input("Please specify a sample type: \"control\" or \"disease\"?"))
            if self.sample_type == "control" or self.sample_type == None:
                samplegroup = self.sample_dict(project = "kollman", feature = "stimulation")["unstimulated"]
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group")["Control"])
                samplegroup.append(self.sample_dict(project = "kollman", feature = "stimulation",
                					nottype = ["unstimulated", "listeria"]))
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group",
                					nottype = ["Control", "DS"]))
            if self.sample_type == "disease":
                samplegroup = self.sample_dict(project = "kollman", feature = "stimulation")["listeria"]
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group")["DS"])

        print "    The sample labels with sample type", self.sample_type, " are:", samplegroup
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
            findQuery = dict({'project': project}.items() + add_query.items())
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
        sample_groups[previous_group] = sample_labels_list    # Do once more after exiting loop
        print sample_groups
        return sample_groups

    def collectbetas(self,
                     window_size = 1):
        '''Collects and bins methylation data'''

        # Bin the beta values and collect average positions
        position_dic = {}
        betasamp_list = []
        count = 0
        for doc in self.docs:
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

        print '    %s probes\' beta values were extracted and binned.' % count

        x_position = []
        y_avg = []
        for pos, tup_list in sorted(position_dic.iteritems()):
            beta_values = []
            for beta, samp in tup_list:
                if self.sample_type == None:
                    beta_values.append(beta)
                elif samp in self.sample_groups:
                    beta_values.append(beta)
                else: break
                data_avg = mean(beta_values)
                x_position.append(pos)
                y_avg.append(data_avg)

        print "    %i beta values collected" % len(x_position)
        self.positions = x_position
        self.betas = y_avg
        return None


    def getwaves(self, tail = 1):
        count = 0
        self.tail = tail
        # This dict will store the position as keys and height and standard deviation as values.
        waves = {}
        # "tail" is min height of a tail to be included in the plot for a peak
        # which doesn't have its center in the region
        for doc in self.docs:
            if isinstance(doc['stddev'], basestring): int()
            pos, height, stddev = doc['pos'], doc['height'], int(doc['stddev'])
            if self.start <= pos <= self.end:
                waves[pos] = [height, stddev]
                count += 1
            else:
                dist_to_region = min(abs(pos - self.end), abs(self.start - pos))
                dist_from_peak_to_tail = sqrt((-2) * stddev * stddev * log(tail / height))
                # print "        ", pos, height, stddev
                # print "        tail distance", dist_from_peak_to_tail
                # print "        dist to region", dist_to_region
                if dist_from_peak_to_tail - dist_to_region >= 0:
                    waves[pos] = [height, stddev]
                    count += 1
                # else: print "         Not included:    ", pos, height, stddev,
        print " Only %i peaks were found in region." % count
        self.waves = waves
        self.Query['waves'] = waves
        return None

#    def compare(self):
#        '''NOT RUNNING ATM'''
#        self.finddocs()
#        self.waves2 = self.getwaves()
#        return None

    def svg(self, filename = None, color = None, to_string = False):
        if self.collection == "methylation":
            if color == None: color = "indigo"
            drawing = self.drawgene(filename = filename, color = color)
        if self.collection == "waves":
            if color == None: color = "indigo"
            drawing = self.drawpeaks(filename = filename, color = color)

        if filename == None or to_string:
            return drawing.tostring()
        if filename and not to_string:
            print " Making svg file \"%s\"\n" % filename
            drawing.save()
            return None

    def drawgene(self,
                    filename,
                    color):
        '''Make svg drawing. This function is not to b called directly, only by svg() and svgtostring() '''
        X, Y = self.positions, self.betas

        smooth = False
        offset = X[0]
        invertby = max(Y)

        X = [round(float(item - offset) / 20000, 3) + 20 for item in X]
        Y = [round((invertby - item) * 1000, 2) + 20 for item in Y]

        # d is the list of coordinates with commands such as
        # M for "move to' to initiate curve and S for smooth curve
        d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
        if smooth: d = d + "S"
        for i in range(2, len(X)):
            d = d + (" " + str(X[i]) + "," + str(Y[i]))

        length, width = str(X[-1]), str(max(Y))

        gene = Drawing("SVGs/" + filename,
        		size = (str(float(length) + 10) + "mm", str(float(width) + 10) + "mm"),
        		viewBox = ("0 0 " + str(float(length) + 10) + " " + str(float(width) + 10)),
        		preserveAspectRatio = "xMinYMin meet")
        gene.add(Path(stroke = color, fill = "none", d = d))
        return gene

    def drawpeaks(self,
                       filename = "peaks.svg",
                       color = "indigo"):
        '''Make svg drawing for peaks
        Code below needs cleaning and commenting:
            + adjust heigh of peaks
            + add y-tics
            + plot 2 queries!
        '''
        waves = self.waves
        colors = {'indigo':'slateblue', 'red':'orange'}
        color = 'indigo'
        fillcolor = colors['indigo']
        # if self.waves2:
        #    waves2 = self.waves2
        #    color = 'red'
        #    fillcolor = colors['red']
        tail = self.tail
        start = self.start
        offset = start
        end = self.end
        length = 200.0
        width = 60.0
        margin = 20.0
        scale_x = length / (end - start)
        waves = self.waves
        peaks = Drawing("SVGs/" + filename,
        		size = (str(length) + "mm " , str(width) + "mm"),
        		viewBox = ("0 0 " + str(length + margin + 30) + " " + str(width + margin + 30)),
        		preserveAspectRatio = "xMinYMin meet")

        def makegaussian(start, end, margin, length, pos, tail, offset, height, stddev):
            X = []
            endpts = int((sqrt((-2) * stddev * stddev * log(tail / height))))
            for i in range (-stddev, stddev, 3):
                X.append(float(i))
            for i in range (-endpts, -stddev, 5):
                X.append(float(i))
            for i in range (stddev, endpts, 5):
                X.append(float(i))
            if (endpts) not in X: X.append(endpts)
            X.sort()
            X = [float(x) for x in X]
            X = [x for x in X if 0 <= (x + pos - offset) < (end - start)]
            stddev = float(stddev)
            Y = [round(height * exp(-x * x / (2 * stddev * stddev)), 2) for x in X]

            return X, Y

        heights = []
        for pos, [height, stddev] in sorted(waves.iteritems()):
            heights.append(height)
        maxh = max(heights)
        scale_y = (width + margin) * 0.8 / maxh
        for pos, [height, stddev] in sorted(waves.iteritems()):
            print "Peak", pos, height, stddev
            X, Y = makegaussian(start, end, margin, length, pos, tail, offset, float(height), stddev)
            X = [round((x - offset + pos) * scale_x, 2) + 20 for x in X]
            for x in X:
                if x < (margin + 0.5):
                    X.insert(0, margin)
                    Y.insert(0, tail)
                    break
                if x > (margin + length - 0.5):
                    X.append(margin + length)
                    Y.append(tail)
                    break
            # Scale Y and inverse the coordinates
            Y = [round(y * scale_y, 2) for y in Y]
            Y = [((width + margin) * 0.8 + margin - y) for y in Y]
            # d is the list of coordinates with commands such as
            # M for "move to' to initiate curve and S for smooth curve
            d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
            for i in range(2, len(X)):
                d = d + (" " + str(X[i]) + "," + str(Y[i]))
            # print "    " , d
            peaks.add(Path(stroke = color, stroke_width = 0.1,
            		stroke_linecap = 'round', stroke_opacity = 0.8,
            		fill = "slateblue", fill_opacity = 0.5, d = d))


        peaks.add(Text("Chipseq Peaks", insert = (margin, margin - 10.0),
        		fill = "midnightblue", font_size = "5"))
        scale_tics = 1;
        while((scale_tics * 10) < end - start):
            scale_tics *= 10;
        xtics = [i for i in range(start, end + 1) if i % (scale_tics) == 0]
        if len(xtics) < 4: xtics += [i for i in range(start, end + 1) if i % (scale_tics / 2) == 0 and i not in xtics]
        for tic in xtics:
            tic_x = (margin + (tic - offset) * scale_x)
            tic_y = width + margin * 2
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            ticline = Rect(insert = (tic_x, width + margin * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            peaks.add(ticline)
            peaks.add(ticmarker)

#         Add y tics
#          ytics = [i for i in range(1, int(max(heights))) if i%4 ==0]
#          ytics.append(0)
#          for tic in ytics:
#              ticline = Rect(insert=(margin-5-1,margin-8+tic), size = (2,0.1), fill="midnightblue")
#              peaks.add(ticline)
#
        x_axis = Rect(insert = (margin - 5, width + margin * 2 - 5),
        		size = ((end - start) * scale_x + 10, 0.1),
        		fill = "midnightblue")
        y_axis = Rect(insert = (margin - 5, margin - 8),
        	size = (0.1, width + margin + 3),
        	fill = "midnightblue")
        peaks.add(x_axis)
        peaks.add(y_axis)

        return peaks
