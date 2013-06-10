'''
Created on 2013-06-10

@author: sperez
'''

from svgwrite.shapes import Rect
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path


class MethylationPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, X, Y, start, end):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.filename = filename
        self.X = X
        self.Y = Y
        self.start = start
        self.end = end

        self.colors = [('indigo', 'slateblue'), ('red', 'orange'),
                  ('green', 'limegreen'), ('orange', 'yellow')]

        self.length = 200.0
        self.width = 60.0
        self.margin = 20.0

        # create drawing
        self.plot = Drawing(filename,
                        size = (str(self.length) + "mm " , str(self.width) + "mm"),
                        viewBox = ("0 0 " + str(self.length + self.margin + 30) + " " + str(self.width + self.margin + 30)),
                        preserveAspectRatio = "xMinYMin meet")

    def build(self):
        length, end, start, width, margin = self.length, self.end, self.start, self. width, self.margin

        X, Y = self.X, self.Y

        offset = X[0]
        invertby = max(Y)

        scale_x = 1 / 20000
        scale_y = 1000
        margin = 20.0

        # scale the variables
        X = [round(float(item - offset) * scale_x, 3) + margin for item in X]
        Y = [round((invertby - item) * scale_y, 2) + margin for item in Y]

        length, width = str(X[-1]), str(max(Y))


        # d contains the coordinates that make up the path
        d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
        for i in range(2, len(X)):
            d = d + (" " + str(X[i]) + "," + str(Y[i]))

        self.plot.add(Path(stroke = self.color, fill = "none", d = d))


    def save(self):
        self.plot.save()
        self.plot = None

    def to_string(self):
        return self.plot.tostring()
        self.plot = None

    def add_legends(self):
        ''' Add title, axis, tic marks and labels '''

        self.peaks.add(Text("Methylation Plot", insert = (self.margin, self.margin - 10.0),
                fill = "midnightblue", font_size = "5"))
