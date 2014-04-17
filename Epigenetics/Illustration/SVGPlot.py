'''

This unit of code funtions to generate the SVG image that is used by the browser,
incorporating methylation and/or chip-seq.

Created on 2013-06-10

@author: sperez, sbrown, afejes
'''

from svgwrite.shapes import Rect, Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import fabs
import Color_Palette
import time
from PlotUtilities import add_cpg, get_axis, bigfont, medfont, smallfont, legend_color
import string    # IGNORE:W0402 - string is deprecated, but str does not have a printable set.

class Plot(object):
    '''
    Called by a MongoEpigeneticsWrapper object to plot methylation data.
    '''

    METHYLATION_DOT_RADIUS = 2
    METHYLATION_DISTR_HT_MED = 12.0
    METHYLATION_DISTR_HT_BIG = 24.0
    DISTR_SHIFT = 0
    DISTR_STROKE = 0.75
    BOTTOM_MARGIN = 120    # 120 pixels
    RIGHT_MARGIN = 30
    MARGIN = 30
    GENE_OFFSET = 20
    palette = Color_Palette.ColorPalette()    # APF - reset on each iteration through the sorter.


    def __init__(self):
        '''Simple initiation of all of the self parameters... Does not do anything unexpected.'''
        self.elements = []
        self.title = None
        self.palette.samples_color = {}    # reset the methylation plot colour assignment on initialization.
        self.sample_grouping = {}    # store sample id/sample group.
        self.gausian_colour = {}
        self.last_hash = 0
        self.start = 0
        self.end = 0
        self.width = 200    # default = 200.0

        self.height = 60    # default = 60.0
        self.message = None

        self.dimension_y = 0    # this is the size of the y field
        self.dimension_x = 0
        self.scale_x = 0
        self.y_bottom = 0

        self.scale_y = 0
        self.maxh = 0
        self.plot = None

        self.gene_offset = self.GENE_OFFSET


    def set_properties(self, filename, title, start, end, width, height):
        '''Set the properties of the canvas on which you'll want to generate your image '''
        self.elements = []
        self.title = title
        self.start = start
        self.end = end
        self.width = width    # default = 200.0

        self.height = height    # default = 60.0

        self.dimension_y = self.height - self.MARGIN - self.BOTTOM_MARGIN    # this is the size of the y field
        self.dimension_x = self.width - self.MARGIN - self.RIGHT_MARGIN
        self.scale_x = float(self.dimension_x) / (self.end - self.start)    # this is a scaling variable
        self.y_bottom = str(round(self.dimension_y + self.MARGIN, 2))


        canvas_size = (str(self.width) + "px" , "100%")    # create drawing # Default is 100%,100% - don't override that, as this allows the svg to fit the data and expand as necessary
        self.plot = Drawing(filename , size = canvas_size)
        background = Rect(insert = (0, 0), size = canvas_size, fill = "white")
        self.plot.add(background)

        magic_box = Text(" ", id = "sample_name", insert = ((self.MARGIN + 20), (self.MARGIN + 20)),
                    fill = "black", font_size = medfont)
        self.elements.append(magic_box)

    def set_sample_index(self, types, samples):
        '''overwrite the sample_index to preserve colours from previous set.'''
        self.palette.set_colors_dict(types, samples)

    def get_sample_index(self):
        ''' Return the sample index so that it can be used in HTML'''
        return self.palette.get_colors_dict()

    def get_types_index(self):
        ''' Return the sample index so that it can be used in HTML'''
        return self.palette.get_type_colors()

    def convert_xcoord_to_pos(self, xcoord):
        return round(float(xcoord - self.start) * self.scale_x, 2) + self.MARGIN


    def make_gausian(self, pos, height, stddev, horizontal = True, y_median = 0, sigmas = 3):
        ''' path points will be at (-3stddev,0), (0,height), (3stddev,0)
            Control points at (-1stddev,0), (-1stddev,height), (1stddev,height), (1stddev,0)
         '''
        X = [-sigmas * stddev, -1 * stddev, -1 * stddev, 0, stddev, stddev, sigmas * stddev]
        Y = [0, 0, height, height, height, 0, 0]

        if horizontal == True:
            X = [round((x - self.start + pos) * self.scale_x, 2) + self.MARGIN for x in X]
            # Scale Y and inverse the coordinates
            Y = [round(y1 * self.scale_y, 2) for y1 in Y]
            Y = [(self.height - self.BOTTOM_MARGIN - y2) for y2 in Y]
        else:
            S = [round(((pos - self.start) * self.scale_x) + y + self.MARGIN + self.DISTR_SHIFT, 2) for y in Y]
            Y = [round(((x + y_median) * self.scale_y), 2) for x in X]
            X = S
        d = "M " + str(X[0]) + "," + str(Y[0]) + " C"    # point 1
        for i in range(1, 7):
            d += " " + str(X[i]) + "," + str(Y[i])
        return d


    def filter_waves(self, waves):

        print "len(waves) = ", len(waves)
        i = 0
        while i < len(waves) - 1:
            if i > 0:
                a_pos, a_ht, a_sd = waves[i - 1]
                b_pos, b_ht, _b_sd = waves[i]
                if b_ht < a_ht and b_pos < a_pos + 3 * a_sd:
                    waves.pop(i)
                    continue
            if i < len(waves) - 2:
                a_pos, a_ht, _a_sd = waves[i]
                b_pos, b_ht, b_sd = waves[i + 1]
                if a_ht < b_ht and a_pos < b_pos - 3 * b_sd:
                    waves.pop(i)
                    continue
            i += 1
                # check if wave is larger than the last and should be removed
        return waves




    def make_trace(self, waves):    # pos, height, stddev, horizontal = True, y_median = 0, sigmas = 3):
        ''' path points will be at (-3stddev,0), (0,height), (3stddev,0)
            Control points at (-1stddev,0), (-1stddev,height), (1stddev,height), (1stddev,0)
         '''

        waves = sorted(waves)

        waves = self.filter_waves(waves)


        X = [round((pos - self.start) * self.scale_x, 2) + self.MARGIN for (pos, _height, _stddev) in waves]
            # Scale Y and inverse the coordinates
        Y = [round(height * self.scale_y, 2) for (_pos, height, _stddev)  in waves]
        Y = [(self.height - self.BOTTOM_MARGIN - y2) for y2 in Y]
        S = [round(stddev * self.scale_x, 2) for (_pos, _height, stddev) in waves]



        if (X[0] > S[0]):
            d = "M " + str(X[0] - (2 * S[0])) + "," + self.y_bottom + " C"    # point 1
            d += " " + str(X[0] - (S[0])) + "," + self.y_bottom    # control point 1
            d += " " + str(X[0] - (S[0])) + "," + str(Y[0])    # control point 2
            d += " " + str(X[0]) + "," + str(Y[0])    # actual coordinate
        else:
            d = "M " + str(X[0]) + "," + str(Y[0]) + " C"    # point 1
        for i in range(1, len(X)):
            if ((3 * S[i]) + (3 * S[i - 1])) < (X[i] - X[i - 1]):
                d += " " + str(X[i - 1] + S[i - 1]) + "," + str(Y[i - 1])    # control point 1
                d += " " + str(X[i - 1] + 2 * S[i - 1]) + "," + self.y_bottom    # control point 2
                d += " " + str(X[i - 1] + 3 * S[i - 1]) + "," + self.y_bottom    # actual coordinate

                d += " " + str(X[i] - S[i]) + "," + self.y_bottom    # control point 2
                d += " " + str(X[i] - 2 * S[i]) + "," + self.y_bottom    # control point 1
                d += " " + str(X[i] - 3 * S[i]) + "," + self.y_bottom    # actual coordinate

                d += " " + str(X[i] - (S[i])) + "," + self.y_bottom    # control point 1
                d += " " + str(X[i] - (S[i])) + "," + str(Y[i])    # control point 2
                d += " " + str(X[i]) + "," + str(Y[i])    # actual coordinate

            else:
                d += " " + str(X[i - 1] + round((X[i] - X[i - 1]) / 4, 2)) + "," + str(Y[i - 1])    # control point 1
                d += " " + str(X[i] - round((X[i] - X[i - 1]) / 4, 2)) + "," + str(Y[i])    # control point 2
                d += " " + str(X[i]) + "," + str(Y[i])    # actual coordinate
        last = len(X) - 1
        if (X[last] + (S[last]) < self.dimension_x):
            d += " " + str(X[last] + (S[last])) + "," + str(Y[last])    # control point 1
            d += " " + str(X[last] + (S[last])) + "," + self.y_bottom    # control point 2
            d += " " + str(X[last] + (2 * S[last])) + "," + self.y_bottom    # actual coordinate
            print "last point added"

        return d

    def build_chipseq(self, message, waves, trace):
        '''convert loaded data into svg images'''
        if message:
            Message = Text('[ ' + message + ' ]', insert = (float(self.width) / 3.0, float(self.height) / 2.0),
                    fill = "black", font_size = bigfont * 2)
            self.elements.append(Message)
        heights = []    # create path objects for each peak
        if not waves:
            return

        for (pos, height, stddev, sample_id) in waves:
            heights.append(height)
        self.maxh = max(heights)
        self.scale_y = self.dimension_y / self.maxh

        samples = {}
        if trace:
            for (pos, height, stddev, sample_id) in waves:

                if sample_id in samples:
                    samples[sample_id].append((pos, height, stddev))
                else:
                    samples[sample_id] = []
                    samples[sample_id].append((pos, height, stddev))
            for sampleid in samples:
                w = samples[sampleid]
                d = self.make_trace(w)
                types_color, _new = self.palette.colour_assignment_group(sampleid)
                self.elements.append(Path(stroke = types_color, stroke_width = 1,
                       stroke_linecap = 'round', stroke_opacity = 0.8, d = d, fill = 'none',
                       onmouseover = "evt.target.ownerDocument.getElementById('sample_name').firstChild.data = \'%s\'" %
                                    (''.join(s for s in sampleid if s in string.printable))))
        else:

            for (pos, height, stddev, sample_id) in waves:
                d = self.make_gausian(pos, height, stddev)
                types_color, _new = self.palette.colour_assignment_group(sample_id)
                self.elements.append(Path(stroke = types_color, stroke_width = 0.1,
                           stroke_linecap = 'round', stroke_opacity = 0.8,
                           fill = types_color, fill_opacity = 0.5, d = d,
                        onmouseover = "evt.target.ownerDocument.getElementById('sample_name').firstChild.data = \'%s\'" %
                                    (''.join(s for s in sample_id if s in string.printable))))

        # fix to truncate curves at border (to hide them)
        self.elements.append(Rect(insert = (0, self.BOTTOM_MARGIN), size = (self.MARGIN + 1, self.height - self.MARGIN), stroke = types_color, stroke_width = 0.0, fill = "#ffffff", fill_opacity = 1))
        self.elements.append(Rect(insert = (self.width - self.RIGHT_MARGIN, 0), size = (self.RIGHT_MARGIN, self.height - self.MARGIN), stroke = types_color, stroke_width = 0.0, fill = "#ffffff", fill_opacity = 1))
        self.palette.purge_unused()

    def build_methylation(self, message, pos_betas_dict, sample_peaks, show_points, show_peaks, show_groups, probes_by_pos, probe_details, bigger_dists):
        '''convert this information into elements of the svg image'''
        self.scale_y = 1

        ht = 0
        if bigger_dists:
            ht = self.METHYLATION_DISTR_HT_BIG
        else:
            ht = self.METHYLATION_DISTR_HT_MED

        if message:
            Message = Text('[ ' + message + ' ]', insert = (float(self.width) / 3.0, float(self.height) / 2.0),
                    fill = "black", font_size = bigfont * 2)
            self.elements.append(Message)

        for position in pos_betas_dict.keys():
            x = round(float(position - self.start) * self.scale_x, 2) + self.MARGIN

            probeid = probes_by_pos[position]

            if show_points:
                for beta, sample_id, sample_type in pos_betas_dict[position]:
                    sample_id = str(sample_id)
                    sample_type = str(sample_type)
                    y = round((1 - beta) * self.dimension_y, 2) + self.MARGIN
                    type_color, sample_color, new = self.palette.colour_assignment(sample_type, sample_id)
                    if new:
                        show_groups.append(sample_type)
                    if not show_groups or sample_type in show_groups:
                        point = Circle(center = (x, y), r = self.METHYLATION_DOT_RADIUS, fill = sample_color,
                                   onmouseover = "evt.target.ownerDocument.getElementById('sample_name').firstChild.data = \'%s %s-%s \'" %
                                    (probeid, sample_type, sample_id))
                        self.elements.append(point)

            if show_peaks:
                for sample_type in sample_peaks[position]:
                    if not show_groups or sample_type in show_groups:
                        if self.gausian_colour.has_key(sample_type):
                            type_color = self.gausian_colour[sample_type]
                        else:
                            type_color, new = self.palette.colour_assignment_group(sample_type)
                            self.gausian_colour[sample_type] = type_color
                        m, s = sample_peaks[position][sample_type]
                        m = round((1 - m) * self.dimension_y, 2) + self.MARGIN
                        s = round(s * self.dimension_y, 3)



                        if s != 0.0:
                            d = self.make_gausian(position, ht, s, False, m)
                            gaussian = (Path(stroke = type_color,
                                             stroke_width = self.DISTR_STROKE,
                                             stroke_linecap = 'round',
                                             stroke_opacity = 0.8,
                                             fill = type_color,
                                             fill_opacity = 0.1,
                                           d = d))

                            self.elements.insert(1, gaussian)



            # fix to truncate curves at border (to hide them)
        if show_peaks:
            self.elements.append(Rect(insert = (0, 0), size = (self.width, self.MARGIN), stroke_width = 0, fill = "#ffffff", fill_opacity = 1))
            self.elements.append(Rect(insert = (0, self.height - self.BOTTOM_MARGIN), size = (self.width, self.dimension_x - self.height), stroke_width = 0, fill = "#ffffff", fill_opacity = 1))

        for position in pos_betas_dict.keys():
            probeid = probes_by_pos[position]
            x = round(float(position - self.start) * self.scale_x, 2) + self.MARGIN
            if probe_details[probeid]['n_snpcpg'] > 0:    # must process this after the rect, which would cover them otherwise
                point = Rect(insert = (x - 1.0, self.MARGIN + self.dimension_y), size = (2.0, 8.0), stroke_width = 0, fill = 'red',
                               onmouseover = "evt.target.ownerDocument.getElementById('sample_name').firstChild.data = \'SNP in cpg: %s\'" %
                                    (probeid))
                self.elements.append(point)
            elif probe_details[probeid]['n_snpprobe'] > 0:
                point = Rect(insert = (x - 1.0, self.MARGIN + self.dimension_y), size = (2.0, 8.0), stroke_width = 0, fill = 'blue',
                               onmouseover = "evt.target.ownerDocument.getElementById('sample_name').firstChild.data = \'SNP in probe %s\'" %
                                    (probeid))
                self.elements.append(point)
        self.palette.purge_unused()

    def save(self):
        ''' push loaded elements to the the plot, clear out the elements. '''
        for element in self.elements:
            self.plot.add(element)
        self.elements = None    # may want to remove this, if we ever want to do fancy stuff with the elements.
        self.plot.save()

    def to_string(self):
        ''' convert the loaded elements to strings and return the list of elements'''
        t0 = time.time()
        temp = []
        temp.append(self.plot.tostring().replace("</svg>", ""))
        for element in self.elements:
            temp.append(element.tostring())
        temp.append("</svg>")
        print " Conversion of SVG to string took %f seconds" % (time.time() - t0)
        return ''.join(t for t in temp)


    def get_elements(self):
        ''' call sample labels and delete loaded elements. '''
        self.add_sample_labels(self.MARGIN * 3.2 + self.width)
        return self.elements

    def get_xml(self):
        ''' Convert the loaded elements into XML strings and then return them.'''
        strings = ""
        for element in self.elements:
            strings += (element.get_xml().decode('utf-8'))
        return strings

    def add_legends(self, get_cpg, annotations):
        ''' Add annotations, title, axis, tic marks and labels '''

        Title = Text(self.title, insert = (bigfont + ((float(self.MARGIN) - bigfont) / 3),
                                           bigfont + ((float(self.MARGIN) - bigfont) / 3)),
                                           fill = legend_color, font_size = bigfont)
        self.elements.append(Title)

        for axis in get_axis(self.width, self.MARGIN, self.height, self.BOTTOM_MARGIN, self.RIGHT_MARGIN):
            self.elements.append(axis)

        # print "add_legends, messages are: %s" % self.message

        if self.message is None:
            self.add_xtics()
            # self.add_sample_labels(self.width - self.RIGHT_MARGIN + 20)
            if get_cpg:
                for cpg in add_cpg(annotations, self.MARGIN, self.height, self.scale_x, self.start, self.end, self.BOTTOM_MARGIN):
                    self.elements.insert(0, cpg)

    def add_xtics(self):
        ''' Create X tics on the plot'''
        scale_tics = 1

        while((scale_tics * 10) < self.end - self.start):
            scale_tics *= 10
        xtics = [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [j for j in range(self.start, self.end + 1) if j % (scale_tics) == 0 and j not in xtics]
        xtics.sort()
        spacing = fabs((self.MARGIN + (xtics[1] - self.start) * self.scale_x) - (self.MARGIN + (xtics[0] - self.start) * self.scale_x)) / 4
        for tic in xtics:
            tic_x = (self.MARGIN + (tic - self.start) * self.scale_x)
            tic_y = self.height - self.BOTTOM_MARGIN + smallfont * 1.5
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = legend_color, font_size = smallfont))
            ticline = Rect(insert = (tic_x, self.height - self.BOTTOM_MARGIN - 2), size = (1, 5), fill = legend_color)
            for i in range (1, 4):
                if tic_x - spacing * i > self.MARGIN - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, self.height - self.BOTTOM_MARGIN - 2), size = (1, 2), fill = legend_color)
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics_chipseq(self):
        ''' Add Y ticks to the svg plot '''

        if self.maxh: steps = round(self.maxh / 5, 1)
        labels = [0, steps, 2 * steps, 3 * steps, 4 * steps, 5 * steps]
        ytics = [round(self.height - self.BOTTOM_MARGIN - (self.dimension_y / 5 * y), 3) for y in range(0, 6)]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic, label in zip(ytics, labels):
            ticline = Rect(insert = (self.MARGIN - 2, tic), size = (5, 1), fill = legend_color)
            if tic - spacing > self.MARGIN:
                ticline2 = Rect(insert = (self.MARGIN - 2, tic - spacing), size = (2, 1), fill = legend_color)
                self.elements.append(ticline2)
            tic_x = self.MARGIN - smallfont * 2
            tic_y = tic + 1
            if len(str(label)) == 1:
                tic_x = tic_x + 3
            if len(str(label)) == 2:
                tic_x = tic_x + 2
            if len(str(label)) >= 3:
                tic_x = tic_x - 10
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = legend_color, font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics_methylation(self):
        ''' Add Y ticks to the svg plot '''
        labels = [0, 0.2, 0.4, 0.6, 0.8, 1]
        ytics = [round((self.MARGIN + self.dimension_y) - (y * self.dimension_y), 3) for y in labels]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic, label in zip(ytics, labels):

            ticline = Rect(insert = (self.width - self.RIGHT_MARGIN, tic), size = (5, 1), fill = legend_color)
            if tic - spacing > self.MARGIN:
                ticline2 = Rect(insert = (self.width - self.RIGHT_MARGIN, tic - spacing), size = (2, 1), fill = legend_color)
                self.elements.append(ticline2)
            tic_x = self.width - self.RIGHT_MARGIN + smallfont
            tic_y = tic + 1
            if len(str(label)) == 1:
                tic_x = tic_x + 3
            if len(str(label)) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = legend_color, font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def draw_genes(self, genes):
        for gene in genes:
            for transcript in gene['transcripts']:

                start = self.convert_xcoord_to_pos(gene['start'])
                length = self.convert_xcoord_to_pos(gene['end']) - start
                if start < self.MARGIN:
                    if start < 0:    # first, remove anything before zero.
                        length += start
                        start = 0
                    length -= (self.MARGIN + start)    # then remove anything before the margin begins
                    start = self.MARGIN
                if start + length > (self.width - self.RIGHT_MARGIN):
                    length = (self.width - self.RIGHT_MARGIN) - start
                text = None
                if gene['strand'] == 1:
                    text = gene['name'] + " ->>>"
                else:
                    text = " <<<- " + gene['name']
                # print "(self.width + self.RIGHT_MARGIN + self.MARGIN)", (self.width - self.RIGHT_MARGIN)
                # print "gene -> text:%s chrend:%i chrstart:%i start:%i length:%i" % (gene['name'], gene['end'], gene['start'], start, length)
                g = Rect(insert = (start, self.height - self.BOTTOM_MARGIN + self.gene_offset + 4), size = (length, 2), fill = "grey")
                t = (Text(text, insert = (start, self.height - self.BOTTOM_MARGIN + self.gene_offset + 9), fill = legend_color, font_size = smallfont))
                self.elements.append(g)

                for exon in gene["transcripts"][transcript]["exons"]:
                    e = gene["transcripts"][transcript]["exons"][exon]
                    e_start = self.convert_xcoord_to_pos(e["start"])
                    e_len = self.convert_xcoord_to_pos(e['end']) - e_start
                    if e_start > (self.width - self.RIGHT_MARGIN) or (e_start + e_len) < self.MARGIN:
                        continue
                    if e_start < self.MARGIN:
                        e_start = self.MARGIN
                    if e_start + e_len > (self.width - self.RIGHT_MARGIN):
                        e_len = (self.width - self.RIGHT_MARGIN) - e_start

                    e = Rect(insert = (e_start, self.height - self.BOTTOM_MARGIN + self.gene_offset), size = (e_len, 9), fill = "grey")
                    self.elements.append(e)

                self.elements.append(t)
                self.gene_offset += 12
                if self.gene_offset > 250:
                    self.gene_offset = self.GENE_OFFSET


