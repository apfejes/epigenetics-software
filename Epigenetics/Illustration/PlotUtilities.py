'''
Created on 2013-08-07

@author: sperez
'''

from svgwrite.shapes import Rect
from svgwrite.text import Text


def get_axis(start, end, margin, width, axis_x_margin, axis_y_margin, scale_x):
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
        y1 = axis_y_margin + width
        length = margin
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
    
    for ((a,b),c) in annotations['Islands']:
        #print 'island', a,b,c
        if a < start: a = start
        if b > end: b = end
        x1 = margin + (a-start)*scale_x
        y1 = axis_y_margin
        length = y1 + width + margin -10
        thickness = (b-a)*scale_x
        #print x1, length, y1
        
        if 'IC' in c:
            color = 'limegreen'
        if 'HC' in c:
            color = 'darkgreen'
    
    
        island = Rect(insert = (x1, y1), 
                       size = (thickness,length),
                       fill = color, 
                       fill_opacity = 0.4)
        elements.append(island)
    
    return elements
