'''
Created on 2013-06-07

@author: sperez
'''
from svgwrite.shapes import Rect
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path

from math import exp, sqrt, fabs, log

from PlotUtilities import get_axis, add_cpg, add_tss, bigfont, medfont, smallfont

class ChipseqPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, title, message, waves, start, end, 

                 annotations, length, margin, width):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []

        self.title = title
        self.waves = waves
        self.start = start
        self.end = end
        self.length = length    # default = 200.0
        self.margin = margin    # default = 20.0
        self.width = width    # default = 60.0
        self.annotations = annotations
        self.message = message

        self.colors = [('indigo', 'slateblue'), ('red', 'orange'),
                  ('green', 'limegreen'), ('orange', 'yellow')]

        # create drawing
        size = (str(self.length) + "mm" , str(self.width * 1.5) + "mm")
        self.plot = Drawing(filename, size = size,
                        viewBox = ("0 0 " + str(self.length) + " " + str(self.width + self.margin * 4)),
                        preserveAspectRatio = "xMinYMin meet")
        background = Rect(insert = (0, 0), size = size, fill = "white")
        self.plot.add(background)

        self.axis_x_margin = None
        self.scale_x = None
        self.maxh = None
        self.scale_y = None
        self.offset_y = None
        self.samples_color = None
        self.axis_y_margin = None

        if message:
            Message = Text('[ ' + message + ' ]', insert = ((self.margin + self.length) / 3, self.margin + self.width / 2),
                    fill = "black", font_size = 12)
            self.elements.append(Message)
        else:
            self.build()


    def build(self):

        self.scale_x = self.length / (self.end - self.start)
        tail = 1

        # create path objects for each peak
        heights = []
        for (pos, height, stddev, sample_id) in self.waves:
            heights.append(height)
        self.maxh = max(heights)
        self.scale_y = (self.width + self.margin) * 0.8 / self.maxh
        self.offset_y = (self.width + self.margin) * 0.8 + self.margin

        sample_count = 0
        samples_color = {}
        for (pos, height, stddev, sample_id) in self.waves:
            print "    Peak", pos, height, stddev
            X, Y = self.makegaussian(self.start, self.end, pos, tail, self.start, float(height), stddev)
            X = [round((x - self.start + pos) * self.scale_x, 2) + 20 for x in X]
            for x in X:
                if x < (self.margin + 1):
                    X.insert(0, self.margin)
                    Y.insert(0, tail)
                    break
                if x > (self.margin + self.length - 1):
                    X.append(self.margin + self.length)
                    Y.append(tail)
                    break
            # Scale Y and inverse the coordinates
            Y = [round(y * self.scale_y, 2) for y in Y]
            Y = [(self.offset_y - y) for y in Y]
            # d is the list of coordinates with commands such as
            # M for "move to' to initiate curve and S for smooth curve
            d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
            for i in range(2, len(X)):
                d += (" " + str(X[i]) + "," + str(Y[i]))

            if sample_id not in samples_color :
                sample_count += 1
                samples_color[sample_id] = self.colors[sample_count - 1]


            peak = (Path(stroke = samples_color[sample_id][0], stroke_width = 0.1,
                           stroke_linecap = 'round', stroke_opacity = 0.8,
                           fill = samples_color[sample_id][1], fill_opacity = 0.5, d = d))

            self.elements.append(peak)
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
        self.add_sample_labels(self.margin * 3.2 + self.length)
        return self.elements

    def add_data(self, foreign_elements):
        '''TODO: add docstring'''
        if not isinstance(foreign_elements, list):
            raise ValueError("Data to add to plot should be stored in a list, not a {}".format(type(foreign_elements)))
        for element in foreign_elements:
            self.elements.append(element)
        print "% i svg elements have been added to the current svg object." % len(foreign_elements)

    def add_legends(self, get_tss, get_cpg):
        ''' Add title, axis, tic marks and labels '''
        if self.title is None:
            self.title = "Chipseq Peaks"
        Title = Text(self.title, insert = (self.margin / 3, self.margin / 3),
                fill = "midnightblue", font_size = bigfont)
        self.elements.append(Title)

        for axis in get_axis(self.start, self.end, self.length, self.margin, self.width, self.axis_x_margin, self.axis_y_margin):
            self.elements.append(axis)

        if self.message is '':
            self.add_xtics()
            self.add_ytics()
            self.add_sample_labels(self.margin * 2 + self.length)
            if get_tss:
                for tss in add_tss(self.annotations, self.margin, self.width, self.scale_x, self.start, self.end, self.axis_x_margin, self.axis_y_margin):
                    self.elements.append(tss)
            if get_cpg:
                for cpg in add_cpg(self.annotations, self.margin, self.width, self.scale_x, self.start, self.end, self.axis_x_margin, self.axis_y_margin):
                    self.elements.append(cpg)


    def add_sample_labels(self, x_position):
        '''TODO: add docstring'''
        if len(self.samples_color) > 20:
            fontsize = str(float(medfont) - 0.5)
        elif len(self.samples_color) < 5:
            fontsize = str(float(medfont) + 0.5)
        else: fontsize = medfont

        spacing = 0.1
        y_position = self.margin

        for sample, color in self.samples_color.iteritems():
            label = Text(sample, insert = (x_position, y_position),
                                            fill = color[1], font_size = fontsize)
            y_position += float(fontsize) + spacing
            self.elements.append(label)
        return None


    @staticmethod
    def makegaussian(start, end, pos, tail, offset, height, stddev):
        '''TODO: Add docstring'''
        endpts = int((sqrt((-2) * stddev * stddev * log(float(tail) / height))))
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
        Y = [round(height * exp(-x * x / (2 * stddev * stddev)), 2) for x in X]
        return X, Y

    def add_xtics(self):
        '''TODO: add docstring'''
        # offset is self.start
        scale_tics = 1

        while((scale_tics * 10) < self.end - self.start):
            scale_tics *= 10
        xtics = [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((self.margin + (xtics[1] - self.start) * self.scale_x) - (self.margin + (xtics[0] - self.start) * self.scale_x)) / 4
        for tic in xtics:
            tic_x = (self.margin + (tic - self.start) * self.scale_x)
            tic_y = self.width + self.margin * 2
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            ticline = Rect(insert = (tic_x, self.margin + self.margin * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            for i in range (1, 4):

                if tic_x - spacing * i > self.margin - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, self.width + self.margin * 2 - 5 - 1), size = (0.1, 1), fill = "midnightblue")
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics(self):
        '''TODO: add docstring'''
        scale_tics = 64
        ytics = [i for i in range(0, int(self.maxh) + 1, scale_tics)]
        while len(ytics) < 4:
            scale_tics /= 2
            ytics += [i for i in range(0, int(self.maxh) + 1, scale_tics) if i not in ytics]
        ytics = [round(self.offset_y - y * self.scale_y, 3) for y in ytics]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic in ytics:
            ticline = Rect(insert = (self.margin - 5 - 1, tic), size = (2, 0.1), fill = "midnightblue")
            ticline2 = Rect(insert = (self.margin - 5, tic + spacing), size = (1, 0.1), fill = "midnightblue")
            tic_x = self.margin - 13
            tic_y = tic + 1
            label = str(int(round((self.offset_y - tic) / self.scale_y)))
            if len(label) == 1:
                tic_x += 3
            if len(label) == 2:
                tic_x += 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)
