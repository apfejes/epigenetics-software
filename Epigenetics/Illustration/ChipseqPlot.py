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
    def __init__(self, filename, title, waves, start, end, 
                 annotations, LENGTH, MARGIN, WIDTH):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []

        self.title = title
        self.waves = waves
        self.start = start
        self.end = end
        self.length = LENGTH    # default = 200.0
        self.margin = MARGIN    # default = 20.0
        self.width = WIDTH    # default = 60.0
        self.annotations = annotations

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
        
        self.build()


    def build(self):
        LENGTH, end, start, WIDTH, MARGIN = self.length, self.end, self.start, self. width, self.margin
        waves = self.waves
        offset = start
        self.scale_x = LENGTH / (end - start)
        tail = 1

        # create path objects for each peak
        heights = []
        for (pos, height, stddev, sample_id) in waves:
            heights.append(height)
        maxh = max(heights)
        self.maxh = maxh
        scale_y = (WIDTH + MARGIN) * 0.8 / maxh
        offset_y = (WIDTH + MARGIN) * 0.8 + MARGIN
        self.scale_y, self.offset_y = scale_y, offset_y

        sample_count = 0
        samples_color = {}
        for (pos, height, stddev, sample_id) in waves:
            print "    Peak", pos, height, stddev
            X, Y = self.makegaussian(start, end, MARGIN, LENGTH, pos, tail, offset, float(height), stddev)
            X = [round((x - offset + pos) * self.scale_x, 2) + 20 for x in X]
            for x in X:
                if x < (MARGIN + 1):
                    X.insert(0, MARGIN)
                    Y.insert(0, tail)
                    break
                if x > (MARGIN + LENGTH - 1):
                    X.append(MARGIN + LENGTH)
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
                samples_color[sample_id] = self.colors[sample_count - 1]


            peak = (Path(stroke = samples_color[sample_id][0], stroke_width = 0.1,
                           stroke_linecap = 'round', stroke_opacity = 0.8,
                           fill = samples_color[sample_id][1], fill_opacity = 0.5, d = d))

            self.elements.append(peak)
        self.samples_color = samples_color


    def save(self):
        for element in self.elements:
            self.plot.add(element)
        self.plot.save()

    def to_string(self):
        for element in self.elements:
            self.plot.add(element)
        z = self.plot.tostring()
        self.plot = None
        return z

    def get_elements(self):
        self.add_sample_labels(self.margin * 3.2 + self.length)
        z = self.elements
        self.elements = None
        return z

    def add_data(self, elements = None):
        elements_to_add = elements
        if not isinstance(elements_to_add, list):
            raise ValueError("Data to add to plot should be stored in a list, not a {}".format(type(elements)))
        for element in elements_to_add:
            self.plot.add(element)
        print "% i svg elements have been added to the current svg object." % len(elements)

    def add_legends(self,get_tss, get_cpg):
        ''' Add title, axis, tic marks and labels '''
        if self.title is None:
            self.title = "Chipseq Peaks"
        Title = Text(self.title, insert = (self.margin/3, self.margin/3),
                fill = "midnightblue", font_size = bigfont)
        self.elements.append(Title)

        self.add_xtics()
        self.add_ytics()
        self.add_axis()
        self.add_sample_labels(self.margin * 2 + self.length)
        for axis in get_axis(self.start, self.end, self.length, self.margin, self.width, self.axis_x_margin, self.axis_y_margin):
            self.elements.append(axis)
        if get_tss:
            for tss in add_tss(self.annotations, self.margin, self.width, self.scale_x, self.start, self.end, self.axis_x_margin, self.axis_y_margin):
                self.elements.append(tss)
        if get_cpg:
            for cpg in add_cpg(self.annotations, self.margin, self.width, self.scale_x, self.start, self.end, self.axis_x_margin, self.axis_y_margin):
                self.elements.append(cpg)


    def add_sample_labels(self, x_position):
        if len(self.samples_color) > 20:
            fontsize = str(float(medfont)-0.5)
        elif len(self.samples_color) < 5:
            fontsize = str(float(medfont)+0.5)
        else: fontsize = medfont

        spacing = 0.1
        y_position = self.margin

        for sample, color in self.samples_color.iteritems():
            label = Text(sample, insert = (x_position, y_position),
                                            fill = color[1], font_size = fontsize)
            y_position += float(fontsize) + spacing
            self.elements.append(label)
        return None

    def makegaussian(self, start,
                     end, MARGIN, LENGTH,
                     pos, tail, offset,
                     height, stddev):
        '''To do: remove LENGTH and MARGIN, or use them'''
        endpts = int((sqrt((-2) * stddev * stddev * log(tail / height))))
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
        if (endpts) not in X: X.append(endpts)
        X.sort()
        X = [float(x) for x in X if 0 <= (x + pos - offset) < (end - start)]
        stddev = float(stddev)
        Y = [round(height * exp(-x * x / (2 * stddev * stddev)), 2) for x in X]
        return X, Y

    def add_xtics(self):
        end, start, WIDTH, MARGIN = self.end, self.start, self. width, self.margin
        offset = start
        scale_x = self.scale_x
        scale_tics = 1

        while((scale_tics * 10) < end - start):
            scale_tics *= 10
        xtics = [i for i in range(start, end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [i for i in range(start, end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((MARGIN + (xtics[1] - offset) * scale_x) - (MARGIN + (xtics[0] - offset) * scale_x)) / 4
        for tic in xtics:
            tic_x = (MARGIN + (tic - offset) * scale_x)
            tic_y = WIDTH + MARGIN * 2
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            ticline = Rect(insert = (tic_x, WIDTH + MARGIN * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            for i in range (1, 4):
                if tic_x - spacing * i > MARGIN - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, WIDTH + MARGIN * 2 - 5 - 1), size = (0.1, 1), fill = "midnightblue")
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics(self):
        maxh, MARGIN = self.maxh, self.margin
        scale_y, offset_y = self.scale_y, self.offset_y

        scale_tics = 64
        ytics = [i for i in range(0, int(maxh) + 1, scale_tics)]
        while len(ytics) < 4:
            scale_tics /= 2
            ytics += [i for i in range(0, int(maxh) + 1, scale_tics) if i not in ytics]
        ytics = [round(offset_y - y * scale_y, 3) for y in ytics]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic in ytics:
            ticline = Rect(insert = (MARGIN - 5 - 1, tic), size = (2, 0.1), fill = "midnightblue")
            ticline2 = Rect(insert = (MARGIN - 5, tic + spacing), size = (1, 0.1), fill = "midnightblue")
            tic_x = MARGIN - 13
            tic_y = tic + 1
            label = str(int(round((offset_y - tic) / scale_y)))
            if len(label) == 1:
                tic_x = tic_x + 3
            if len(label) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)

    def add_axis(self):
        MARGIN = self.margin
        WIDTH = self.width
        axis_x_margin = MARGIN - 5
        self.axis_x_margin = axis_x_margin
        axis_y_margin = MARGIN - 8
        self.axis_y_margin = axis_y_margin
        x_axis = Rect(insert = (axis_x_margin, WIDTH + MARGIN + axis_x_margin),
                size = ((self.end - self.start) * self.scale_x + 10, 0.1),
                fill = "midnightblue")
        y_axis = Rect(insert = (axis_x_margin, axis_y_margin),
            size = (0.1, WIDTH + MARGIN + 3),
            fill = "midnightblue")
        self.elements.append(x_axis)
        self.elements.append(y_axis)

