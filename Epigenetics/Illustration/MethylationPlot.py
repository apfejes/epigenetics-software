'''
Created on 2013-06-10

@author: sperez
'''

from svgwrite.shapes import Rect, Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import fabs


class MethylationPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, title, X, Y, color, start, end):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.title = title
        self.X = X
        self.Y = Y
        self.color = color
        self.start = start
        self.end = end

        self.length = 200.0
        self.width = 60.0
        self.margin = 20.0

        # create drawing
        self.plot = Drawing(filename,
                        size = (str(self.length) + "mm " , str(self.width) + "mm"),
                        viewBox = ("0 0 " + str(self.length + self.margin + 30) + " " + str(self.width + self.margin + 30)),
                        preserveAspectRatio = "xMinYMin meet")

    def build(self):
        length, end, start, width, margin = self.length, self.end, self.start, self.width, self. margin

        X, Y = self.X, self.Y

        offset = X[0]
        invertby = max(Y)
        self.offset_y = (width + margin) * 0.8 + margin
        scale_x = length / (end - start)
        self.scale_x = scale_x
        scale_y = (width + margin) * 0.8 / max(Y)
        self.scale_y = scale_y

        # scale the variables
        X = [round(float(item - offset) * scale_x, 3) + margin for item in X]
        Y = [round((invertby - item) * scale_y, 2) + margin for item in Y]



        # d contains the coordinates that make up the path
#         d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
#         for i in range(2, len(X)):
#             d = d + (" " + str(X[i]) + "," + str(Y[i]))
#
#         self.plot.add(Path(stroke = self.color, fill = "none", stroke_width = '0.3', d = d))

        for x, y in zip(X, Y):
            point = Circle(center = (x, y), r = 0.3, fill = self.color)
            self.plot.add(point)

    def save(self):
        self.plot.save()
        self.plot = None

    def to_string(self):
        return self.plot.tostring()
        self.plot = None

    def add_legends(self):
        ''' Add title, axis, tic marks and labels '''
        if self.title == None:
            self.title = "Methylation PLot"
        self.plot.add(Text(self.title, insert = (self.margin, self.margin - 10.0),
                fill = "midnightblue", font_size = "5"))
        self.add_xtics()
        self.add_ytics()
        self.add_axis()


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
                    self.plot.add(ticline2)
            self.plot.add(ticline)
            self.plot.add(ticmarker)

    def add_ytics(self):
        maxh, margin = max(self.Y), self.margin
        scale_y, offset_y = self.scale_y, self.offset_y
        ytics = [0, 0.2, 0.4, 0.6, 0.8, 1]
        ytics = [round(offset_y - y * scale_y, 3) for y in ytics]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic in ytics:
            ticline = Rect(insert = (margin - 5 - 1, tic), size = (2, 0.1), fill = "midnightblue")
            ticline2 = Rect(insert = (margin - 5, tic - spacing), size = (1, 0.1), fill = "midnightblue")
            tic_x = margin - 13
            tic_y = tic + 1
            label = str(round((offset_y - tic) / scale_y, 1))
            if len(label) == 1:
                tic_x = tic_x + 3
            if len(label) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            self.plot.add(ticline)
            self.plot.add(ticline2)
            self.plot.add(ticmarker)

    def add_axis(self):
        margin = self.margin
        width = self.width
        x_axis = Rect(insert = (margin - 5, width + margin * 2 - 5),
                size = ((self.end - self.start) * self.scale_x + 10, 0.1),
                fill = "midnightblue")
        y_axis = Rect(insert = (margin - 5, margin - 8),
            size = (0.1, width + margin + 3),
            fill = "midnightblue")
        self.plot.add(x_axis)
        self.plot.add(y_axis)
