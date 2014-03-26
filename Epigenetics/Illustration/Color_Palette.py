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
        self.counter = {}    # keeps track of last assigned colour for each colour (self.colors) map.
        self.types_color = {}
        self.samples_color = {}
        self.colors = {}
        self.keys_inuse = []

        # Hold dictionaries of colours for use in generating svgs
#         self.colors['blue'] = ['blue', 'cornflowerblue', 'darkblue', 'deepskyblue', 'darkturquoise',
#                        'midnightblue', 'navy', 'dodgerblue', 'lightblue', 'lightskyblue', 'cadetblue', 'teal',
#                        'paleturquoise', 'aquamarine', 'azure', 'aqua', 'lightsteelblue', 'powderblue']
#         self.colors['green'] = ['lightseagreen', 'limegreen', 'lawngreen', 'olivedrab', 'chartreuse', 'mediumturquoise',
#                                'mediumspringgreen', 'forestgreen', 'seagreen', 'palegreen', 'olive', 'darkcyan',
#                                'yellowgreen', 'darkolivegreen', 'darkgreen', 'darkseagreen', 'lime']
#         self.colors['red'] = ['orangered', 'tomato', 'orange', 'gold', 'firebrick', 'sandybrown',
#                              'lightcoral', 'crimson', 'coral', 'darkred', 'indianred', 'maroon']
#         self.colors['purple'] = ['darkslategrey', 'orchid', 'magenta', 'purple', 'blueviolet', 'darkviolet',
#                            'pink', 'mediumslateblue', 'lightpink', 'deeppink', 'indigo', 'lavenderblush',
#                            'violet', 'mediumorchid', 'mediumpurple', 'thistle', 'darkmagenta', 'plum']


        # self.colors['#FF00FF'] = ['#ffccff', '#ffb9ff', '#ffa7ff', '#ff94ff', '#ff82ff', '#ff6fff', '#ff5dff', '#ff4aff', '#ff38ff', '#ff25ff', '#ff13ff', '#ff00ff']    # magenta
        # self.colors['#FF0000'] = ['#ffcccc', '#ffb9b9', '#ffa7a7', '#ff9494', '#ff8282', '#ff6f6f', '#ff5d5d', '#ff4a4a', '#ff3838', '#ff2525', '#ff1313', '#ff0000']    # red
        # self.colors['#00FF00'] = ['#00cc00', '#0FCF0F', '#1DD21D', '#2CD52C', '#3BD83B', '#4ADB4A', '#58DD58', '#67E067', '#76E376', '#85E685', '#93E993', '#A2ECA2']    # green
        # self.colors['#0000ff'] = ['#ccccff', '#b9b9ff', '#a7a7ff', '#9494ff', '#8282ff', '#6f6fff', '#5d5dff', '#4a4aff', '#3838ff', '#2525ff', '#1313ff', '#0000ff']    # blue
        # self.colors['#00ffff'] = ['#ccffff', '#b9ffff', '#a7ffff', '#94ffff', '#82ffff', '#6fffff', '#5dffff', '#4affff', '#38ffff', '#25ffff', '#13ffff', '#00ffff']    # light blue
        # self.colors['#CCCC00'] = ['#cccc00', '#BFC000', '#B1B400', '#A4A700', '#969B00', '#898F00', '#7B8300', '#6E7700', '#606B00', '#535E00', '#455200', '#384600']    # yellows-> greens
        self.colors['red'] = ['#a30000', '#730000', '#b80000', '#660000', '#cc0000', '#520000', '#e00000', '#3d0000', '#ff0a0a', '#290000', '#ff3333' ]
        self.colors['blue'] = ['#0000a3', '#0000b8', '#00008f', '#0000cc', '#00007a', '#0000e0', '#0000f5', '#0000ff', '#1f1fff', '#3333ff', '#4747ff']
        self.colors['green'] = ['#00a300', '#008f00', '#002900', '#006600', '#008000', '#005200', '#00b800', '#003d00', '#00cc00', '#00e000', '#33ff33']
        self.colors['purple'] = ['#8f008f', '#a300a3', '#800080', '#b800b8', '#660066', '#cc00cc', '#520052', '#e000e0', '#3d003d', '#290029', '#ff0aff']
        # yellow
        self.colors['#b8b800'] = ['#666600', '#7a7a00', '#525200', '#8f8f00', '#3d3d00', '#cccc00']
        self.colors['grey'] = ['#5c5c5c', '#525252', '#666666', '#474747', '#707070', '#3d3d3d', '#7a7a7a', '#333333', '#808080', '#292929', '#8f8f8f']
        self.colors['cyan'] = ['#00a3a3', '#00b8b8', '#00cccc', '#008f8f', '#00e0e0', '#007a7a', '#00f5f5', '#006666', '#70ffff', '#005252', '#40bfbf']
        self.colors['orange'] = ['#8f5d00', '#a36a00', '#b87700', '#7a5000', '#cc8500', '#664200', '#e09200', '#523500', '#f59f00', '#3d2800', '#ffa500']
        # self.colors[''] = ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']


        self.color_wheel = {}

        for i, j in enumerate(self.colors):
            self.color_wheel[1 + i] = j
            # print "colour_wheel %i - %s" % (1 + i, j)

    def _increment_type_counter(self):
        '''self.counter keeps track of the next group colour to assign to new groups.'''
        self.type_count += 1
        if self.type_count > len(self.color_wheel.keys()):    # this array has no zero, 1 to len(), therefore not >= len()
            self.type_count = 1
        return None

    def _increment_sample_counter(self, sample_type):
        '''self.counter keeps track of the next sample colour to assign for each sample type.'''
        self.counter[sample_type] += 1
        if self.counter[sample_type] >= len(self.colors[self.types_color[sample_type]]):
            self.counter[sample_type] = 0
        return None

    def key_inuse(self, key):
        if key not in self.keys_inuse:
            self.keys_inuse.append(key)
        return

    def purge_unused(self):
        for key in self.types_color.keys():
            if key not in self.keys_inuse:
                self.types_color.pop(key)
        for key in self.samples_color.keys():
            if key not in self.keys_inuse:
                self.samples_color.pop(key)
        self.keys_inuse = []
        return

    def colour_assignment(self, sample_type, sample_name):
        '''assign colours for individual samples.  If the group doesn't already have a colour, assign that too.'''

        key = "%s-%s" % (sample_type, sample_name)
        # work out if the type has a color palette
        type_colour, new = self.colour_assignment_group(sample_type)
        self.key_inuse(key)
        if key not in self.samples_color:
            self.samples_color[key] = self.colors[self.types_color[sample_type]][self.counter[sample_type]]
            self._increment_sample_counter(sample_type)
        sample_colour = self.samples_color[key]

        return type_colour, sample_colour, new

    def colour_assignment_group(self, sample_type):
        '''assign a colour to a group - used by groups in methylation, and used for Waves, which are all the same colour'''
        new = False
        self.key_inuse(sample_type)
        if sample_type not in self.types_color:
            self._increment_type_counter()
            self.types_color[sample_type] = self.color_wheel[self.type_count]
            self.counter[sample_type] = 0
            new = True
        if sample_type not in self.counter:    # check, just in case colours were passed, but the sample counter has been reset.
            self.counter[sample_type] = 0
        type_colour = self.types_color.get(sample_type)
        return type_colour, new

    def get_colours(self, sample_type, sample_id):
        '''Simple method for retrieving colours we should already have in the palette.'''
        return self.types_color[sample_type], self.samples_color[sample_id]

    def get_group_colour(self, sample_type):
        '''Simple method for retrieving colours we should already have in the palette.'''
        return self.types_color[sample_type]

    def get_type_colors(self):
        '''get colours for all types'''
        return self.types_color

    def get_colors_dict(self):
        '''return the list of colour/sample mappings'''
        return self.samples_color

    def set_colors_dict(self, types_index, samples):
        '''return the list of colour/sample mappings'''
        self.samples_color = samples
        self.types_color = types_index




