'''
Created on 2013-06-07

@author: sperez
'''
from svgwrite.shapes import Rect
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path

from math import exp, sqrt, fabs, log

class ChipseqPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, title, waves, start, end, length, margin, width):
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

        self.colors = [('indigo', 'slateblue'), ('red', 'orange'),
                  ('green', 'limegreen'), ('orange', 'yellow')]

        # create drawing
        self.plot = Drawing(filename,
                        size = (str(self.length) + "mm" , str(self.width * 1.5) + "mm"),
                        viewBox = ("0 0 " + str(self.length) + " " + str(self.width + self.margin * 2)),
                        preserveAspectRatio = "xMinYMin meet")

    def build(self):
        length, end, start, width, margin = self.length, self.end, self.start, self. width, self.margin
        waves = self.waves
        offset = start
        self.scale_x = length / (end - start)
        tail = 1

        # create path objects for each peak
        heights = []
        for (pos, height, stddev, sample_id) in waves:
            heights.append(height)
        maxh = max(heights)
        self.maxh = maxh
        scale_y = (width + margin) * 0.8 / maxh
        offset_y = (width + margin) * 0.8 + margin
        self.scale_y, self.offset_y = scale_y, offset_y

        sample_count = 0
        samples_color = {}
        for (pos, height, stddev, sample_id) in waves:
            print "    Peak", pos, height, stddev
            X, Y = self.makegaussian(start, end, margin, length, pos, tail, offset, float(height), stddev)
            X = [round((x - offset + pos) * self.scale_x, 2) + 20 for x in X]
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
                samples_color[sample_id] = self.colors[sample_count - 1]


            peak = (Path(stroke = samples_color[sample_id][0], stroke_width = 0.1,
                           stroke_linecap = 'round', stroke_opacity = 0.8,
                           fill = samples_color[sample_id][1], fill_opacity = 0.5, d = d))

            self.elements.append(peak)


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

    def add_legends(self):
        ''' Add title, axis, tic marks and labels '''
        if self.title == None:
            self.title = "Chipseq Peaks"
        Title = Text(self.title, insert = (self.margin, self.margin - 10.0),
                fill = "midnightblue", font_size = "5")
        self.elements.append(Title)
        self.add_xtics()
        self.add_ytics()
        self.add_axis()


    def makegaussian(self, start,
                     end, margin, length,
                     pos, tail, offset,
                     height, stddev):
        X = []
        endpts = int((sqrt((-2) * stddev * stddev * log(tail / height))))
        for i in range (-stddev, stddev, 10):
            X.append(float(i))
        for i in range (-endpts, -stddev, 20):
            X.append(float(i))
        for i in range (stddev, endpts, 20):
            X.append(float(i))
        if (endpts) not in X: X.append(endpts)
        X.sort()
        X = [float(x) for x in X]
        X = [x for x in X if 0 <= (x + pos - offset) < (end - start)]
        stddev = float(stddev)
        Y = [round(height * exp(-x * x / (2 * stddev * stddev)), 2) for x in X]
        return X, Y

    def add_xtics(self):
        end, start, width, margin = self.end, self.start, self. width, self.margin
        offset = start
        scale_x = self.scale_x
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
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            ticline = Rect(insert = (tic_x, width + margin * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            for i in range (1, 4):
                if tic_x - spacing * i > margin - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, width + margin * 2 - 5 - 1), size = (0.1, 1), fill = "midnightblue")
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics(self):
        maxh, margin = self.maxh, self.margin
        scale_y, offset_y = self.scale_y, self.offset_y

        scale_tics = 60
        ytics = [i for i in range(0, int(maxh) + 1, scale_tics)]
        while len(ytics) < 4:
            scale_tics /= 2
            ytics += [i for i in range(0, int(maxh) + 1, scale_tics) if i not in ytics]
        ytics = [round(offset_y - y * scale_y, 3) for y in ytics]
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
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)

    def add_axis(self):
        margin = self.margin
        width = self.width
        x_axis = Rect(insert = (margin - 5, width + margin * 2 - 5),
                size = ((self.end - self.start) * self.scale_x + 10, 0.1),
                fill = "midnightblue")
        y_axis = Rect(insert = (margin - 5, margin - 8),
            size = (0.1, width + margin + 3),
            fill = "midnightblue")
        self.elements.append(x_axis)
        self.elements.append(y_axis)

