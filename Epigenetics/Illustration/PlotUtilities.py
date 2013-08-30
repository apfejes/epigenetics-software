'''
Created on 2013-08-07

@author: sperez
'''

from svgwrite.shapes import Rect
from svgwrite.text import Text

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
    return (x_axis, y_axis)


def add_tss(annotations, margin, height, scale_x, offset_x, bottom_margin):
    if annotations is None:
        return []
    annotations = annotations
    spacing_gene = smallfont
    spacing_tss = smallfont * 2.5

    offset_y = 0
    elements = []
    x1 = 0
    font_size = medfont
    between_tss = font_size * 7

    # Add TSS line if there is in fact a TSS in this region
    TSSs = annotations['TSS'].keys()
    TSSs.sort()

    for tss in TSSs:
        gene_name = annotations['TSS'][tss]
        # print 'TSS:', gene_name, tss
        previous_x1 = x1
        x1 = margin + (tss - offset_x) * scale_x
        y1 = height - bottom_margin
        thickness = 0.8
        color = 'dodgerblue'

        if offset_y > spacing_tss * 2 or (between_tss + previous_x1) < x1 :
            offset_y = 0

        length = float(bottom_margin) / 3.0 + offset_y + smallfont

        TSSline = Rect(insert = (x1, y1),
                       size = (thickness, length),
                       fill = color, fill_opacity = 0.4)
        TSS = (Text((str(tss)), insert = (x1 + 1, length + y1), fill = color, font_size = font_size - 1, fill_opacity = 0.6))
        gene = (Text(gene_name, insert = (x1 + 1, length + y1 - spacing_gene), fill = color, font_size = font_size, fill_opacity = 0.8))
        offset_y += spacing_tss

        elements.append(TSSline)
        elements.append(TSS)
        elements.append(gene)

    return elements



def add_cpg(annotations, margin, height, width, scale_x, start, end, bottom_margin, right_margin):
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
        
    elements.append(Text("High Density CpG Island", insert = (width - right_margin + medfont*3, height - bottom_margin + medfont*2), fill = legend_color, font_size = medfont, fill_opacity = 0.8))
    elements.append(Text("Intermediate Density CpG Island", insert = (width - right_margin + medfont*3, height - bottom_margin + medfont*4), fill = legend_color, font_size = medfont, fill_opacity = 0.8))
    elements.append(Rect(insert = (width - right_margin + medfont, height -bottom_margin + medfont),
                       size = (medfont,medfont),
                       fill = color_high,
                       fill_opacity = 0.3))

    elements.append(Rect(insert = (width - right_margin + medfont, height - bottom_margin + medfont*3),
                       size = (medfont,medfont), 
                       fill = color_low,
                       fill_opacity = 0.3))
    
    return elements
