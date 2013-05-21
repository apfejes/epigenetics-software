#from svgwrite.shapes import Polyline
#from svgwrite.shapes import Rect
#from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path

#Drawing a methylation plot
gene = Drawing("SVGs/methylation.svg", size=("400mm","50mm"), viewBox=('0 0 100 20'), preserveAspectRatio="xMinYMin meet")

#d is the list of coordinates with commands such as
#M for "move to' to initiate curve and S for smooth curve
d = "M2,3 3,5S 4,8 5,9 6,10 7,9 8,8 9,8 10,6 11,5"
p = Path(stroke = "blue", fill = "none", d = d)
gene.add(p)



gene.save()
print "The methylation data is ready to be viewed." 

