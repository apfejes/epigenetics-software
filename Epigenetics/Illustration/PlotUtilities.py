'''
Created on 2013-08-07

@author: sperez
'''

from svgwrite.shapes import Rect
from svgwrite.text import Text


def get_axis(end, start, margin, width, axis_x_margin, axis_y_margin, scale_x):
    margin = margin
    width = width
    axis_x_margin = margin - 5
    axis_x_margin = axis_x_margin
    axis_y_margin = margin - 8
    axis_y_margin = axis_y_margin 
    x_axis = Rect(insert = (axis_x_margin, width + margin + axis_x_margin),
            size = ((end - start) * scale_x + 10, 0.1),
            fill = "midnightblue")
    y_axis = Rect(insert = (axis_x_margin, axis_y_margin),
        size = (0.1, width + margin + 3),
        fill = "midnightblue")
    
    return (x_axis, y_axis)
    

def get_annotations(annotations, margin, width, scale_x, start, end, axis_x_margin, axis_y_margin):
    annotations = annotations
    margin = margin
    width = width
    spacing = 9
    offset = 0 
    elements = []
    
    
    #Add TSS line if there is in fact a TSS in this region
    for (gene,tss) in annotations['TSS']:
        #print 'TSS:', gene, tss
        x1 = margin + (tss-start)*scale_x
        y1 = axis_y_margin
        length = width + margin*3
        thickness = 0.3
        color = 'dodgerblue'
    
        TSSline = Rect(insert = (x1, y1), 
                       size = (thickness, length),
                       fill = color)
        TSS = (Text((str(tss)), insert = (x1+1, length+y1), fill = color, font_size = "4"))
        gene = (Text("--> " + gene + " gene", insert = (x1, length+y1-spacing/2), fill = color, font_size = "4"))
        offset += spacing
        if offset > spacing*5: offset = 0
        elements.append(TSSline)
        elements.append(TSS)
        elements.append(gene)
    
    for (a,b) in annotations['Islands']:
        print 'island', a,b
        if a < start: a = start
        if b > end: b = end
        height = 3
        length = (b-a)*scale_x
        x1 = margin + (a-start)*scale_x
        y1 = width + margin*2 -height - 5
        #print x1, length, y1
        color = 'hotpink'
    
        island = Rect(insert = (x1, y1), 
                       size = (length,height),
                       fill = color)
        elements.append(island)
    
    return elements