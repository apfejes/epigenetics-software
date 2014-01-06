'''
Created on 2013-08-07

@author: sperez
'''

from svgwrite.shapes import Rect

bigfont = 20
medfont = 14
smallfont = 10
legend_color = 'black'

def get_axis(width, margin, height, bottom_margin, right_margin):
    '''leave "margin" on either side of the image, draw the axes along the 
    boundaries of the margin.'''
    margin = margin
    height = height
    x_axis = Rect(insert = (margin, height - bottom_margin),
            size = (width - (margin + right_margin), 1),
            fill = legend_color)
    y_axis = Rect(insert = (margin, margin),
        size = (1, height - (margin + bottom_margin)),    # viewing area is the height, minus the top margin and bottom margin.
        fill = legend_color)
    y_axis2 = Rect(insert = (width - right_margin, margin),
        size = (1, height - (margin + bottom_margin)),    # viewing area is the height, minus the top margin and bottom margin.
        fill = legend_color)
    return (x_axis, y_axis, y_axis2)


def add_cpg(annotations, margin, height, scale_x, start, end, bottom_margin):
    '''draw the cpg islands on the svg graph.'''
    if annotations is None:
        return []
    elements = []

    color_high = 'darkseagreen'
    color_low = 'deepskyblue'
    for ((a, b), c) in annotations['Islands']:
        if a < start:
            a = start
        if b > end:
            b = end
        x1 = margin + (a - start) * scale_x
        thickness = (b - a) * scale_x

        if 'IC' in c:
            color = color_low
            opacity = 0.2
        if 'HC' in c:
            color = color_high
            opacity = 0.2
        island = Rect(insert = (x1, margin),
                       size = (thickness, height - margin - bottom_margin),
                       fill = color,
                       fill_opacity = opacity)
        elements.append(island)

    # elements.append(Text("High Density CpG Island", insert = (width - right_margin + medfont*3, height - bottom_margin + medfont*2), fill = legend_color, font_size = medfont, fill_opacity = 0.8))
    # elements.append(Text("Intermediate Density CpG Island", insert = (width - right_margin + medfont*3, height - bottom_margin + medfont*4), fill = legend_color, font_size = medfont, fill_opacity = 0.8))
#     elements.append(Rect(insert = (width - right_margin + medfont, height - bottom_margin + medfont),
#                        size = (medfont, medfont),
#                        fill = color_high,
#                        fill_opacity = 0.3))
#
#     elements.append(Rect(insert = (width - right_margin + medfont, height - bottom_margin + medfont * 3),
#                        size = (medfont, medfont),
#                        fill = color_low,
#                        fill_opacity = 0.3))

    return elements
