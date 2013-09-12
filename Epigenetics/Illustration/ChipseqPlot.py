'''
Created on 2013-06-07

@author: sperez
'''
from svgwrite.shapes import Rect
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path

from math import exp, sqrt, fabs, log

from PlotUtilities import get_axis, add_cpg, add_tss, bigfont, medfont, smallfont, legend_color

class ChipseqPlot(object):
    '''
    Called by a MongoEpigeneticsWrapper object to plot ChIP-Seq data.
    '''

    DISTR_STROKE = 0.5
    BOTTOM_MARGIN = 100    # 100 pixels
    RIGHT_MARGIN = 240
    MARGIN = 30


    def __init__(self, filename, title, message, waves, start, end,
                 annotations, width, height):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []

        self.title = title
        self.waves = waves
        self.start = start
        self.end = end
        self.width = width    # default = 200.0
        self.annotations = annotations
        self.message = message

        self.height = height    # default = 60.0
        self.colors = [('indigo', 'slateblue'), ('red', 'orange'),
                  ('green', 'limegreen'), ('orange', 'yellow')]

        self.dimension_y = self.height - self.MARGIN - self.BOTTOM_MARGIN    # this is the size of the y field
        self.dimension_x = self.width - self.MARGIN - self.RIGHT_MARGIN
        self.scale_x = float(self.dimension_x) / (self.end - self.start)    # this is a scaling variable


        size = (str(self.width) + "px" , str(self.height) + "px")
        # create drawing
        self.plot = Drawing(filename, size = size
                            # , viewBox = ("0 0 " + str(self.height) + " " + str(self.width + (self.margin * 2)))
                            # , preserveAspectRatio = "xMinYMin meet"
                            )
        background = Rect(insert = (0, 0), size = size, fill = "white")
        self.plot.add(background)

        if message:
            Message = Text('[ ' + message + ' ]', insert = (float(self.width) / 3.0, float(self.height) / 2.0),
                    fill = legend_color, font_size = bigfont * 2)
            self.elements.append(Message)
        else:
            self.build()


    def build(self):
        tail = 1

        # create path objects for each peak
        heights = []
        for (pos, height, stddev, sample_id) in self.waves:
            heights.append(height)
        self.maxh = max(heights)
        self.scale_y = self.dimension_y / self.maxh

        sample_count = 0
        samples_color = {}
        for (pos, height, stddev, sample_id) in self.waves:
            # print "    Peak", pos, height, stddev
            X, Y = self.makegaussian(self.start, self.end, pos, tail, self.start, float(height), stddev)
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


    def save(self):
        '''TODO: add docstring'''
        for element in self.elements:
            self.plot.add(element)
        self.elements = None    # may want to remove this, if we ever want to do fancy stuff with the elements.
        self.plot.save()

    def to_string(self):
        '''TODO: add docstring'''
        for element in self.elements:
            self.plot.add(element)
        z = self.plot.tostring()
        self.plot = None
        return z

    def get_elements(self):
        '''TODO: add docstring'''
        self.add_sample_labels(self.MARGIN * 3.2 + self.width)
        return self.elements

    def add_data(self, foreign_elements):
        '''TODO: add docstring'''
        if not isinstance(foreign_elements, list):
            raise ValueError("Data to add to plot should be stored in a list, not a {}".format(type(foreign_elements)))
        for element in foreign_elements:
            self.elements.append(element)
        print "% i svg elements have been added to the current svg object." % len(foreign_elements)

    def add_legends(self, get_tss, get_cpg):
        ''' Add annotations, title, axis, tic marks and labels '''
        if self.title is None:
            self.title = "ChIP-Seq PLot"
        Title = Text(self.title, insert = (bigfont + ((float(self.MARGIN) - bigfont) / 3),
                                           bigfont + ((float(self.MARGIN) - bigfont) / 3)),
                                           fill = legend_color, font_size = bigfont)
        self.elements.append(Title)

        for axis in get_axis(self.width, self.MARGIN, self.height, self.BOTTOM_MARGIN, self.RIGHT_MARGIN):
            self.elements.append(axis)

        if self.message is '':
            self.add_xtics()
            self.add_ytics()
            self.add_sample_labels(self.width - self.RIGHT_MARGIN + 10)
            if get_tss:
                for tss in add_tss(self.annotations, self.MARGIN, self.height, self.scale_x, self.start, self.BOTTOM_MARGIN):
                    self.elements.append(tss)
            if get_cpg:
                for cpg in add_cpg(self.annotations, self.MARGIN, self.height, self.width, self.scale_x, self.start, self.end, self.BOTTOM_MARGIN, self.RIGHT_MARGIN):
                    self.elements.append(cpg)


    def add_sample_labels(self, x_position = None):
        ''' TODO: fill in docstring '''
        if x_position == None:
            x_position = self.width - self.RIGHT_MARGIN + self.RIGHT_MARGIN / 2
        if len(self.samples_color) > 20:
            fontsize = str(float(medfont) - 0.5)
        elif len(self.samples_color) < 5:
            fontsize = str(float(medfont) + 0.5)
        else: fontsize = medfont

        spacing = 0.1
        y_position = self.MARGIN + bigfont

        for sample, color in self.samples_color.iteritems():
            label = Text(sample, insert = (x_position, y_position),
                                            fill = color[1], font_size = fontsize)
            y_position += float(fontsize) + spacing
            self.elements.append(label)
        return None

    def add_xtics(self):
        '''TODO: add docstring'''
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

    def add_ytics(self):
        '''TODO: add docstring'''
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

    @staticmethod
    def makegaussian(start, end, pos, tail, offset, innerheight, stddev):
        '''TODO: Add docstring'''
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
