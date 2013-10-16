'''
Created on 2013-06-10

@author: sperez
'''

from svgwrite.shapes import Rect, Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import fabs, exp, sqrt, log
import Color_Palette
from PlotUtilities import add_cpg, add_tss, get_axis, bigfont, smallfont, legend_color
# from PlotUtilities import medfont

class Plot(object):
    '''
    Called by a MongoEpigeneticsWrapper object to plot methylation data.
    '''

    METHYLATION_DOT_RADIUS = 2
    METHYLATION_DISTR_HT = 12.0
    DISTR_STROKE = 0.5
    BOTTOM_MARGIN = 120    # 120 pixels
    RIGHT_MARGIN = 240
    MARGIN = 30
    palette = Color_Palette.ColorPalette()    # APF - reset on each iteration through the sorter.
    colors = [('indigo', 'slateblue'), ('red', 'orange'),
                  ('green', 'limegreen'), ('orange', 'yellow')]



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

        # create drawing
        canvas_size = (str(self.width) + "px" , str(self.height) + "px")
        self.plot = Drawing(filename, size = canvas_size)
        background = Rect(insert = (0, 0), size = canvas_size, fill = "white")
        self.plot.add(background)

    def set_sample_index(self, index, types):
        '''overwrite the sample_index to preserve colours from previous set.'''
        self.palette.set_colors_dict(types, index)

    def get_sample_index(self):
        ''' Return the sample index so that it can be used in HTML'''
        return self.palette.get_colors_dict()

    def get_types_index(self):
        ''' Return the sample index so that it can be used in HTML'''
        return self.palette.get_type_colors()


    def build_chipseq(self, message, waves):
        '''convert loaded data into svg images'''
        if message:
            Message = Text('[ ' + message + ' ]', insert = (float(self.width) / 3.0, float(self.height) / 2.0),
                    fill = "black", font_size = bigfont * 2)
            self.elements.append(Message)

        tail = 1

        # create path objects for each peak
        heights = []
        for (pos, height, stddev, sample_id) in waves:
            heights.append(height)
        self.maxh = max(heights)
        self.scale_y = self.dimension_y / self.maxh

        sample_count = 0
        samples_color = {}
        for (pos, height, stddev, sample_id) in waves:
            # print "    Peak", pos, height, stddev
            X, Y = self.makegaussian_horizontal(self.start, self.end, pos, tail, self.start, float(height), stddev)
            X = [round((x - self.start + pos) * self.scale_x, 2) + self.MARGIN for x in X]
            for x in X:    # Adjust peaks on the edge of the plotting area so they don't look skewed.
                if x < (self.MARGIN + 1):
                    X.insert(0, self.MARGIN)
                    Y.insert(0, tail)
                    break
                if x > (self.width - 1):
                    X.append(self.width)
                    Y.append(tail)
                    break
            # Scale Y and inverse the coordinates
            Y = [round(y * self.scale_y, 2) for y in Y]
            Y = [(self.height - self.BOTTOM_MARGIN - y) for y in Y]
            # d is the list of coordinates with commands such as
            # M for "move to' to initiate curve and S for smooth curve
            d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
            for i in range(2, len(X)):
                d += (" " + str(X[i]) + "," + str(Y[i]))

            if sample_id not in samples_color :
                sample_count += 1
                samples_color[sample_id] = self.colors[sample_count - 1]


            self.elements.append(Path(stroke = samples_color[sample_id][0], stroke_width = 0.1,
                           stroke_linecap = 'round', stroke_opacity = 0.8,
                           fill = samples_color[sample_id][1], fill_opacity = 0.5, d = d))
        self.samples_color = samples_color

    def build_methylation(self, message, pos_betas_dict, sample_peaks, show_points, show_peaks):
        '''convert this information into elements of the svg image'''
        all_y = []

        if message:
            Message = Text('[ ' + message + ' ]', insert = (float(self.width) / 3.0, float(self.height) / 2.0),
                    fill = "black", font_size = bigfont * 2)
            self.elements.append(Message)


        for position in pos_betas_dict.keys():
            for y, _sample, _sample_type in pos_betas_dict[position]:
                all_y.append(y)
        # self.max_y_value = max(all_y)    # (max y value - value /y height) + margin gives you position
            # / self.max_y_value

        first = True
        for position in pos_betas_dict.keys():
            x = round(float(position - self.start) * self.scale_x, 2) + self.MARGIN

            if show_points:
                for beta, sample_id, sample_type in pos_betas_dict[position]:
                    sample_id = str(sample_id)
                    sample_type = str(sample_type)
                    y = round((1 - beta) * self.dimension_y, 2) + self.MARGIN
                    # print "sample Grouping = %s" % (self.sample_grouping)
                    if self.sample_grouping.has_key("%s-%s" % (sample_type, sample_id)):
                        # print "sample grouping has key (%s)" % (sample_id)
                        type_color, sample_color = self.palette.get_colours(sample_type, sample_id)
                    else:
                        if first:
                            self.palette.set_colors_dict({}, {})    # reset if first key does not exist.
                            first = False
                        # print "sample grouping does not have key (%s)" % ("%s-%s" % (sample_type, sample_id))
                        self.sample_grouping["%s-%s" % (sample_type, sample_id)] = sample_type
                        type_color, sample_color = self.palette.sorter(sample_type, sample_id)
                    point = Circle(center = (x, y), r = self.METHYLATION_DOT_RADIUS, fill = sample_color)
                    self.elements.append(point)

            if show_peaks:
                for sample_type in sample_peaks[position]:
                    if self.gausian_colour.has_key(sample_type):
                        type_color = self.gausian_colour[sample_type]
                    else:
                        type_color = self.palette.assign_group_colour(sample_type)
                        self.gausian_colour[sample_type] = type_color
                    (m, s) = sample_peaks[position][sample_type]
                    m = round((1 - m) * self.dimension_y, 2) + self.MARGIN
                    s = round(s * self.dimension_y, 3)

                    if s != 0.0:
                        gaussian_y, gaussian_x = self.makegaussian_vertical(s, self.METHYLATION_DISTR_HT)    # reverse output arguments for sideways gaussians
                        gaussian_x = [coord + x - 1 for coord in gaussian_x]
                        gaussian_y = [item + m for item in gaussian_y]
                        d = "M"

                        for i in range(0, len(gaussian_x)):
                            d = d + (" " + str(gaussian_x[i]) + "," + str(gaussian_y[i]))

                        gaussian = (Path(stroke = type_color,
                                         stroke_width = self.DISTR_STROKE,
                                         stroke_linecap = 'round',
                                         stroke_opacity = 0.8,
                                         fill = type_color,
                                         fill_opacity = 0.1,
                                       d = d))

                        self.elements.append(gaussian)

    def save(self):
        ''' push loaded elements to the the plot, clear out the elements. '''
        for element in self.elements:
            self.plot.add(element)
        self.elements = None    # may want to remove this, if we ever want to do fancy stuff with the elements.
        self.plot.save()

    def to_string(self):
        ''' convert the loaded elements to strings and return the list of elements'''
        for element in self.elements:
            self.plot.add(element)
        z = self.plot.tostring()
        self.plot = None
        return z

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

    def add_legends(self, get_tss, get_cpg, annotations):
        ''' Add annotations, title, axis, tic marks and labels '''

        Title = Text(self.title, insert = (bigfont + ((float(self.MARGIN) - bigfont) / 3),
                                           bigfont + ((float(self.MARGIN) - bigfont) / 3)),
                                           fill = legend_color, font_size = bigfont)
        self.elements.append(Title)

        for axis in get_axis(self.width, self.MARGIN, self.height, self.BOTTOM_MARGIN, self.RIGHT_MARGIN):
            self.elements.append(axis)

        print "add_legends, messages are: %s" % self.message

        if self.message is None:
            self.add_xtics()

            # TODO: Have both of these run, depending on which data is present
            # self.add_ytics_chipseq()
            self.add_ytics_methylation()

            # self.add_sample_labels(self.width - self.RIGHT_MARGIN + 20)
            if get_tss:
                for tss in add_tss(annotations, self.MARGIN, self.height, self.scale_x, self.start, self.BOTTOM_MARGIN):
                    self.elements.append(tss)
            if get_cpg:
                for cpg in add_cpg(annotations, self.MARGIN, self.height, self.width, self.scale_x, self.start, self.end, self.BOTTOM_MARGIN, self.RIGHT_MARGIN):
                    self.elements.append(cpg)

    def add_xtics(self):
        ''' Create X tics on the plot'''
        scale_tics = 1

        while((scale_tics * 10) < self.end - self.start):
            scale_tics *= 10
        # TODO: fix the line below.
        xtics = [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            # TODO: fix the line below.
            xtics += [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0 and i not in xtics]
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
        scale_tics = 64
        labels = [i for i in range(0, int(self.maxh) + 1, scale_tics)]
        while len(labels) < 4:
            scale_tics /= 2
            labels += [i for i in range(0, int(self.maxh) + 1, scale_tics) if i not in labels]
        ytics = [round(self.height - self.BOTTOM_MARGIN - y * self.scale_y, 3) for y in labels]
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
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = legend_color, font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics_methylation(self):
        ''' Add Y ticks to the svg plot '''
        labels = [0, 0.2, 0.4, 0.6, 0.8, 1]
        ytics = [round((self.MARGIN + self.dimension_y) - (y * self.dimension_y), 3) for y in labels]
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
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = legend_color, font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)

    @staticmethod
    def makegaussian_horizontal(start, end, pos, tail, offset, innerheight, stddev):
        ''' create gausian distributions on the plot '''
        endpts = int((sqrt((-2) * stddev * stddev * log(float(tail) / innerheight))))
        spacing = 64
        n_points = 0
        while n_points < 25 and spacing >= 2:
            X = []
            for i in range (-stddev, stddev, spacing):
                X.append(float(i))
            for i in range (-endpts, -stddev, spacing):
                X.append(float(i))
            for i in range (stddev, endpts, spacing):
                X.append(float(i))
            n_points = len(X)
            spacing /= 2
        if (endpts) not in X:
            X.append(endpts)
        X.sort()
        X = [float(x) for x in X if 0 <= (x + pos - offset) < (end - start)]
        stddev = float(stddev)
        Y = [round(innerheight * exp(-x * x / (2 * stddev * stddev)), 2) for x in X]
        return X, Y

    @staticmethod
    def makegaussian_vertical(stddev, innerheight):
        ''' create gausian distributions on the plot '''
        endpts = (sqrt((-2) * stddev * stddev * log(1.0 / innerheight)))
        X = [0]
        X.extend([round(stddev * 2.0 * (i / 9.0) - stddev, 3) for i in range(0, 10)])    # add 10 points  near mean
        X.extend([round(abs(stddev - endpts) * (i / 4.0) + stddev, 3) for i in range(0, 5)])
        X.extend([round(abs(stddev - endpts) * (i / 4.0) - 2.0 * stddev, 3) for i in range(0, 5)])

        X.sort()
        Y = [round(innerheight * exp(-x ** 2 / (2.0 * stddev * stddev)), 3) for x in X]
        return X, Y
