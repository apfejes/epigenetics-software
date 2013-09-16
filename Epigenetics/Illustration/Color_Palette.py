'''
Created on 2013-07-11

@author: sperez
'''

class ColorPalette():
    '''
    Stores organization of color scheme for each part of plot.
    '''
    def __init__(self):
        self.type_count = 0
        self.counter = {}    # keeps track of
        self.types_color = {}
        self.samples_color = {}
        self.colors = {}

        # Hold dictionaries of colours for use in generating svgs
        self.colors['blue'] = ['blue', 'cornflowerblue', 'darkblue', 'deepskyblue', 'darkturquoise',
                       'midnightblue', 'navy', 'dodgerblue', 'lightblue', 'lightskyblue', 'cadetblue', 'teal',
                       'paleturquoise', 'aquamarine', 'azure', 'aqua', 'lightsteelblue', 'powderblue']
        self.colors['green'] = ['lightseagreen', 'limegreen', 'lawngreen', 'olivedrab', 'chartreuse', 'mediumturquoise',
                               'mediumspringgreen', 'forestgreen', 'seagreen', 'palegreen', 'olive', 'darkcyan',
                               'yellowgreen', 'darkolivegreen', 'darkgreen', 'darkseagreen', 'lime']
        self.colors['red'] = ['orangered', 'tomato', 'orange', 'gold', 'firebrick', 'sandybrown',
                             'lightcoral', 'crimson', 'coral', 'darkred', 'indianred', 'maroon']
        self.colors['purple'] = ['darkslategrey', 'orchid', 'magenta', 'purple', 'blueviolet', 'darkviolet',
                           'pink', 'mediumslateblue', 'lightpink', 'deeppink', 'indigo', 'lavenderblush',
                           'violet', 'mediumorchid', 'mediumpurple', 'thistle', 'darkmagenta', 'plum']
        self.color_wheel = {1:'blue', 2:'red', 4:'purple', 3:'green'}

        # return self.colors, self.color_wheel

    def sorter(self, sample_type, sample_id):
        '''This function appears to assign colours to each sample id, based up on sample type.'''
        # print "counter=%s sample_type=%s sample_id=%s" % (self.counter, sample_type, sample_id)
        if sample_type not in self.types_color:
            self.type_count += 1
            if self.type_count >= len(self.color_wheel.keys()):
                self.type_count = 1
            self.types_color[sample_type] = self.color_wheel[self.type_count]    # Assign a hue to sample_type
            self.counter[sample_type] = 0
            # print 'types:', self.type_count, sample_type, self.color_wheel[self.type_count]
        if sample_id not in self.samples_color:
            self.samples_color[sample_id] = self.colors[self.types_color[sample_type]][self.counter[sample_type]]
            self.counter[sample_type] += 1
            if self.counter[sample_type] >= len(self.colors[self.types_color[sample_type]]):
                self.counter[sample_type] = 0
        # print len(self.colors[self.types_color[sample_type]]), self.colors[self.types_color[sample_type]]
        if self.counter[sample_type] > len(self.colors[self.types_color[sample_type]]):
            print self.counter
            print sample_type, sample_id
            print self.types_color[sample_type]
            print self.counter[sample_type]
            print len(self.colors[self.types_color[sample_type]])
            raise ValueError("Ran out of colours! - sorter")
        sample_color = self.samples_color[sample_id]
        type_color = self.types_color[sample_type]
        # print type_color, sample_color
        return type_color, sample_color

    def assign_group_colour(self, sample_type):
        '''This function appears to assign colours to each sample id, based up on sample type.'''
        print "counter=%s sample_type=%s" % (self.counter, sample_type)
        if sample_type not in self.types_color:
            self.type_count += 1
            if self.type_count >= len(self.color_wheel.keys()):
                self.type_count = 1
            self.types_color[sample_type] = self.color_wheel[self.type_count]    # Assign a hue to sample_type
            self.counter[sample_type] = 0
            # print 'types:', self.type_count, sample_type, self.color_wheel[self.type_count]
        # print len(self.colors[self.types_color[sample_type]]), self.colors[self.types_color[sample_type]]
        if self.counter[sample_type] > len(self.colors[self.types_color[sample_type]]):
            print self.counter
            print sample_type
            print self.types_color[sample_type]
            print self.counter[sample_type]
            print len(self.colors[self.types_color[sample_type]])
            raise ValueError("Ran out of colours! - assign_group_colour")
        type_color = self.types_color[sample_type]
        # print type_color, sample_color
        return type_color


    def get_colours(self, sample_type, sample_id):
        '''Simple method for retrieving colours we should already have in the palette.'''
        return self.types_color[sample_type], self.samples_color[sample_id]

    def get_group_colours(self, sample_type):
        '''Simple method for retrieving colours we should already have in the palette.'''
        return self.types_color[sample_type]

    def colors_dict(self):
        '''return the list of colour/sample mappings'''
        return self.samples_color
