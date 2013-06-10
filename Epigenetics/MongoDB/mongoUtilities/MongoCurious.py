'''
Created on 2013-05-23

@author: sperez

'''
from time import time
import os, sys
from numpy import log, mean
from math import sqrt, exp, fabs
from svgwrite.drawing import Drawing
from svgwrite.text import Text
from svgwrite.shapes import Rect
from svgwrite.path import Path

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)

sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import MongoQuery
sys.path.insert(0, _cur_dir + os.sep + "Illustration")
import Illustration.ChipseqPlot as chipseqplot

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

class MongoCurious():
    '''A class to simplify plotting methylation and chipseq data from a mongo database'''
    def __init__(self,
                database = None):
        '''Connects to database'''
        if database == None:
            raise ValueError("Please specify a database.")
        else: self.database = database
        self.mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, self.database)

    def query(self,
                collection = None,
                chromosome = None,
                start = None,
                end = None,
                sample_type = None,
                sample_label = None,
                sample_id = None,
                project = None):
        '''Stores query inputs and parameters as an instance of MongoQuery'''
        Query = MongoQuery.MongoQuery()
        if collection == None:
            raise ValueError("Please specify a collection.")
        self.collection = collection
        Query['database'] = self.database
        Query['collection'] = self.collection
        Query['project'] = project
        self.project = project
        if chromosome == None:
            raise ValueError("Please specificy a chromosome.")
        if isinstance(chromosome, basestring):
            Query['chromosome'] = chromosome
            self.chromosome = chromosome
        elif isinstance(chromosome, int):
                Query['chromosome'] = 'chr' + str(chromosome)
                self.chromosome = chromosome
        if self.project:
            self.sample_groups = self.creategroups()
            Query['sample groups'] = self.sample_groups
        Query['start'] = start
        self.start = start
        Query['end'] = end
        self.end = end
        Query['sample label'] = sample_label
        self.sample_label = sample_label
        Query['sample type'] = sample_type
        self.sample_type = sample_type
        Query['sample id'] = sample_id
        self.sample_id = sample_id

        self.Query = Query
        return self.Query

    def checkquery(self):
        '''Checks that query inputs are valid'''
        t0 = time()
        self.mongo.ensure_index(self.collection, 'chr')
        print "Checking validity of query inputs..."
        if self.chromosome != None:
            Chromosomes = self.mongo.distinct(self.collection, 'chr')
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

        # Preparing the different parameters of the query depending on the collection chosen
        if self.collection == "methylation":
            query_chr, query_start, query_end, query_samplabel = {}, {}, {}, {}
            if self.chromosome != None: query_chr = {'chr':self.chromosome}
            if self.start != None: query_start = {"start_position":{"$lte":self.end}}
            if self.end != None: query_end = {"end_position":{"$gte":self.start}}
            if self.sample_label != None: query_samplabel = {"sample_label":self.sample_label}
            query = dict(query_chr.items() + query_start.items() + query_end.items() + query_samplabel.items())
            return_chr = {'_id': False, 'beta_value': True,
                          'start_position': True, 'end_position': True,
                          'sample_label': True}
            print "\n Conducting query: "
            print "   Database: %s, Collection: %s" % self.database % self.collection
            print "   Find(", query, ")"
            # Get probes corresponding to query and sort by starting positions for beta value binning
            docs = self.mongo.find(self.collection, query, return_chr).sort('start_position', 1)

        if self.collection == "waves":
            query_chr, query_pos, = {}, {}
            if self.chromosome != None: query_chr = {'chr':self.chromosome}
            if self.start != None and self.end != None:
                extension = 500    # extend the region of query to catch peaks with tails in the region
                query_pos = {"pos":{"$lte":self.end + extension, "$gte":self.start - extension}}
            query = dict(query_chr.items() + query_pos.items())
            return_chr = {'_id': False, 'pos': True,
                          'height': True, 'stddev': True,
                          'sample_id': True}
            print "\n Conducting query: Find(", query, ")"
            # Get documents corresponding to query and sort by inverse peak height for plotting purposes
            docs = self.mongo.find(self.collection, query, return_chr).sort('height', -1)

        if docs.count() == 0:
            print "    WARNING: The following query return zero probes or documents!"
            print "    ---> Find(", query, ")"
            print "     use the checkquery() function to validate the inputs of your query."
            sys.exit()

        print " Found %i probes or documents." % docs.count()
        self.docs = docs
        self.count = self.docs.count()
        self.Query['cursor'] = self.docs
        return None


    def creategroups(self):
        '''
        Separate samples into 'groups' according to a particular feature and sample_type like disease
        or control.
        samplegroup is a list of sample labels with the desired sample_type of that feature.
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
        For a particular feature (for example, disease in Down Syndrome experiments) return a dictionary
        structured as {sample label: sample_type} where sample_type is "control" or "diseased
        '''

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
                else: continue
                data_avg = mean(beta_values)
                x_position.append(pos)
                y_avg.append(data_avg)

        print "    %i beta values collected" % len(x_position)
        self.positions = x_position
        self.betas = y_avg
        return None


    def getwaves(self):
        count = 0
        tail = 1
        # This list will store the tuple (pos,height, std dev, sample id) as a value.
        waves = []
        # "tail" is min height of a tail to be included in the plot for a peak
        # which doesn't have its center in the region
        for doc in self.docs:
#            if isinstance(doc['stddev'], basestring): int()
            pos, height, stddev, sample_id = doc['pos'], doc['height'], int(doc['stddev']), doc['sample_id']
            # append all peaks with a center in the region
            if self.start <= pos <= self.end:
                waves.append((pos, height, stddev, sample_id))
                count += 1
            else:
                dist_to_region = min(abs(pos - self.end), abs(self.start - pos))
                dist_from_peak_to_tail = sqrt((-2) * stddev * stddev * log(tail / height))
                if dist_from_peak_to_tail - dist_to_region >= 0:
                    waves.append((pos, height, stddev, sample_id))
                    count += 1
                # else: print "         Not included:    ", pos, height, stddev,
        print " Only %i peaks were found to occur in region." % count
        self.waves = waves
        self.Query['waves'] = waves
        return None

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
                    color, smooth = False):
        '''Make svg drawing. This function is not to be called directly, only by svg() '''
        X, Y = self.positions, self.betas

        offset = X[0]
        invertby = max(Y)

        scale_x = 1 / 20000
        scale_y = 1000
        margin = 20.0

        # scale the variables
        X = [round(float(item - offset) * scale_x, 3) + margin for item in X]
        Y = [round((invertby - item) * scale_y, 2) + margin for item in Y]

        length, width = str(X[-1]), str(max(Y))

        # create drawing
        gene = Drawing("SVGs/" + filename,
                size = (str(float(length)) + "mm", str(float(width)) + "mm"),
                viewBox = ("0 0 " + str(float(length) + margin) + " " + str(float(width) + margin)),
                preserveAspectRatio = "xMinYMin meet")


        # d contains the coordinates that make up the path
        d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
        if smooth: d = d + "S"
        for i in range(2, len(X)):
            d = d + (" " + str(X[i]) + "," + str(Y[i]))

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
        colors = [('indigo', 'slateblue'), ('red', 'orange'),
                  ('green', 'limegreen'), ('orange', 'yellow')]

        tail = 1
        start = self.start
        offset = start
        end = self.end
        length = 200.0
        width = 60.0
        margin = 20.0
        scale_x = length / (end - start)

        peaks = Drawing("SVGs/" + filename,
                        size = (str(length) + "mm " , str(width) + "mm"),
                        viewBox = ("0 0 " + str(length + margin + 30) + " " + str(width + margin + 30)),
                        preserveAspectRatio = "xMinYMin meet")
#        colorfilter = peaks.defs.add(peaks.filter(start = (margin, margin), size = (width, length), filterUnits = "userSpaceOnUse"))

#        colorblend = colorfilter.feComposite()


        heights = []
        for (pos, height, stddev, sample_id) in waves:
            heights.append(height)
        maxh = max(heights)
        scale_y = (width + margin) * 0.8 / maxh
        offset_y = (width + margin) * 0.8 + margin

        sample_count = 0
        samples_color = {}
        for (pos, height, stddev, sample_id) in waves:
            print "  Peak", pos, height, stddev
            X, Y = makegaussian(start, end, margin, length, pos, tail, offset, float(height), stddev)
            X = [round((x - offset + pos) * scale_x, 2) + 20 for x in X]
            for x in X:
                if x < (margin + 1):
                    X.insert(0, margin)
                    Y.insert(0, tail)
                    break
                if x > (margin + length - 1):
                    X.append(margin + length)
                    Y.append(tail)
                    break
            # Scale Y and inverse the coordinates
            Y = [round(y * scale_y, 2) for y in Y]
            Y = [(offset_y - y) for y in Y]
            # d is the list of coordinates with commands such as
            # M for "move to' to initiate curve and S for smooth curve
            d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
            for i in range(2, len(X)):
                d = d + (" " + str(X[i]) + "," + str(Y[i]))

            if sample_id not in samples_color :
                sample_count += 1
                samples_color[sample_id] = colors[sample_count - 1]


            peak = (Path(stroke = samples_color[sample_id][0], stroke_width = 0.1,
                           stroke_linecap = 'round', stroke_opacity = 0.8,
                           fill = samples_color[sample_id][1], fill_opacity = 0.5, d = d))

            peaks.add(peak)
            # peaks.add(colorblend)


        peaks.add(Text("Chipseq Peaks", insert = (margin, margin - 10.0),
        		fill = "midnightblue", font_size = "5"))
        scale_tics = 1;
        while((scale_tics * 10) < end - start):
            scale_tics *= 10;
        xtics = [i for i in range(start, end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [i for i in range(start, end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((margin + (xtics[1] - offset) * scale_x) - (margin + (xtics[0] - offset) * scale_x)) / 4
        for tic in xtics:
            tic_x = (margin + (tic - offset) * scale_x)
            tic_y = width + margin * 2
            print tic_x, tic_x + spacing
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            ticline = Rect(insert = (tic_x, width + margin * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            for i in range (1, 4):
                if tic_x - spacing * i > margin - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, width + margin * 2 - 5 - 1), size = (0.1, 1), fill = "midnightblue")
                    peaks.add(ticline2)
            peaks.add(ticline)
            peaks.add(ticmarker)

        # Add ytics
        scale_tics = 60
        ytics = [i for i in range(0, int(maxh) + 1, scale_tics)]
        while len(ytics) < 4:
            scale_tics /= 2
            ytics += [i for i in range(0, int(maxh) + 1, scale_tics) if i not in ytics]
        ytics = [round(offset_y - y * scale_y, 3) for y in ytics]
        print ytics
        spacing = (ytics[0] - ytics[1]) / 2
        for tic in ytics:
            ticline = Rect(insert = (margin - 5 - 1, tic), size = (2, 0.1), fill = "midnightblue")
            ticline2 = Rect(insert = (margin - 5, tic + spacing), size = (1, 0.1), fill = "midnightblue")
            tic_x = margin - 13
            tic_y = tic + 1
            label = str(int(round((offset_y - tic) / scale_y)))
            if len(label) == 1:
                tic_x = tic_x + 3
            if len(label) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            peaks.add(ticline)
            peaks.add(ticline2)
            peaks.add(ticmarker)

        x_axis = Rect(insert = (margin - 5, width + margin * 2 - 5),
        		size = ((end - start) * scale_x + 10, 0.1),
        		fill = "midnightblue")
        y_axis = Rect(insert = (margin - 5, margin - 8),
        	size = (0.1, width + margin + 3),
        	fill = "midnightblue")
        peaks.add(x_axis)
        peaks.add(y_axis)

        # feComposite in="SourceGraphic" in2="BackgroundImage" operator="over" result="comp"/
        return peaks


