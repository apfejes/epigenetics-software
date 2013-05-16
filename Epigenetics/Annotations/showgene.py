'''
Created on 2013-05-16

@author: sperez

'''


from svgwrite.shapes import Rect
from svgwrite.drawing import Drawing

gene = Drawing("gene.svg")

gene.add(Rect(insert=(70,70), size = (700,70)))

gene.save()