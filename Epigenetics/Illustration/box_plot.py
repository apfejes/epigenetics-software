from svgwrite.shapes import Rect
from svgwrite.shapes import Line
from svgwrite.shapes import Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing


# We get coordinates from querying ensembl normally but that takes time
# so here is the coordinates of the exons for the huntington gene:
# from query_ensembl import coordinates
# from query_ensembl import name, location

class BoxPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, x_max, y_max, **kwargs):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.filename = filename
        self.x_max = x_max
        self.y_max = y_max
        if kwargs.x_min:
            self.x_min = kwargs.x_min
        else:
            self.x_min = 0
        if kwargs.y_min:
            self.y_min = kwargs.y_min
        else:
            self.y_min = 0
        if kwargs.height:
            self.height = kwargs.height
        else:
            self.height = 1000
        if kwargs.width:
            self.width = kwargs.width
        else:
            self.width = 1000
        if kwargs.debug:
            self.debug = kwargs.debug
        else:
            self.debug = True
        if kwargs.margin_top:
            self.margin_top = kwargs.margin_top
        else:
            self.margin_top = 20
        if kwargs.margin_bottom:
            self.margin_bottom = kwargs.margin_bottom
        else:
            self.margin_bottom = 20
        if kwargs.margin_left:
            self.margin_left = kwargs.margin_left
        else:
            self.margin_left = 20
        if kwargs.margin_right:
            self.margin_right = kwargs.margin_right
        else:
            self.margin_right = 20

        # start drawing object
        plot = Drawing(filename, self.debug)    # , size=('200mm', '150mm'), viewBox=('0 0 200 150'))
        plot.add(Line(start = (self.margin_left, self.margin_top), end = (self.margin_left, self.margin_top + self.height)))
        plot.add(Line(start = (self.margin_left, self.margin_top + self.height), end = (self.margin_left + self.width, self.margin_top + self.height)))

    def add_and_zip_data(self, x, y):
        self.data = zip(x, y)

    def add_data(self, x):
        self.data = x

    def build(self):
        for x, y in self.data:
            self.plot.add(Circle(center = (x, y), r = 1, stroke_width = 0.1,
                            stroke_linecap = 'round', stroke_opacity = 0.8,
                            fill = "dodgerblue", fill_opacity = 0.5))
        self.data = None


    def save(self):
        self.plot.save()

    def to_string(self):
        return self.plot.tostring()

