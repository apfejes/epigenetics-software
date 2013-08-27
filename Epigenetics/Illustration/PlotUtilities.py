'''
Created on 2013-08-07

@author: sperez
'''

from svgwrite.shapes import Rect
from svgwrite.text import Text

bigfont = 7
medfont = 4.5
smallfont = 4

def get_axis(start, end, length, margin, width, axis_x_margin, axis_y_margin):
    margin = margin
    width = width
    axis_x_margin = margin - 5
    axis_x_margin = axis_x_margin
    axis_y_margin = margin - 8
    axis_y_margin = axis_y_margin 
    x_axis = Rect(insert = (axis_x_margin, width + margin + axis_x_margin),
            size = (length + 10, 0.1),
            fill = "midnightblue")
    y_axis = Rect(insert = (axis_x_margin, axis_y_margin),
        size = (0.1, width + margin + 3),
        fill = "midnightblue")
    
    return (x_axis, y_axis)
    

def add_tss(annotations, margin, width, scale_x, start, end, axis_x_margin, axis_y_margin):
    if annotations is None:
        return []
    annotations = annotations
    margin = margin
    width = width
    spacing = 9
    offset = 0 
    elements = []
    x1 = 0
    font_size = smallfont
    between_tss = 13
    
    #Add TSS line if there is in fact a TSS in this region
    TSSs = annotations['TSS'].keys()
    TSSs.sort()
    
    for tss in TSSs:
        gene_name = annotations['TSS'][tss]
        print 'TSS:', gene_name, tss
        previous_x1 = x1
        x1 = margin + (tss-start)*scale_x
        y1 = axis_y_margin + width + margin
        length = margin + offset
        thickness = 0.3
        color = 'dodgerblue'
    
        if offset > spacing*3 or (between_tss + previous_x1) < x1 :
            offset = 0
            
        length = margin + offset

        TSSline = Rect(insert = (x1, y1), 
                       size = (thickness, length),
                       fill = color, fill_opacity = 0.4)
        TSS = (Text((str(tss)), insert = (x1+1, length+y1), fill = color, font_size = font_size-1, fill_opacity = 0.6))
        gene = (Text(gene_name, insert = (x1+1, length+y1-spacing/2), fill = color, font_size = font_size, fill_opacity = 0.8))
        offset += spacing

        elements.append(TSSline)
        elements.append(TSS)
        elements.append(gene)

    return elements



def add_cpg(annotations, margin, width, scale_x, start, end, axis_x_margin, axis_y_margin):
    if annotations is None:
        return []
    annotations = annotations
    margin = margin
    width = width
    elements = []
    x1 = 0
     
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