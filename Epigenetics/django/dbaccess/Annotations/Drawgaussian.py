

from numpy import log
from svgwrite.drawing import Drawing
from svgwrite.text import Text
from svgwrite.path import Path
from svgwrite.shapes import Rect
from math import sqrt, exp

#replace
#waves to self. waves
#start to self. start

waves = {36993: [13.33, 72], 29250: [12.54, 19], 29573: [15.8, 25], 37153: [18.52, 79], 29489: [26.22, 38], 28712: [18.43, 79], 37950: [6,120]}
filename = "peaks.svg"
smooth = True
color = "indigo"

def makegaussian(start, end, margin, length, pos, tail, offset, height, stddev):
    X=[]
    endpts =int((sqrt((-2)*stddev*stddev*log(tail/height))))
    for i in range (-stddev,stddev,1):
        X.append(float(i))
    for i in range (-endpts, -stddev,5):
        X.append(float(i))
    for i in range (stddev,endpts,5):
        X.append(float(i))
    if (endpts) not in X: X.append(endpts)
    X.sort()
    X = [float(x) for x in X]
    X = [x for x in X if 0<=(x+pos-offset)<(end-start)]
    stddev = float(stddev)
    Y = [round(height*exp(-x*x/(2*stddev*stddev)),2) for x in X]
    return X,Y
    


tail =1.0
start = 28800
offset = start
end = 38001
length = 200.0
height  =  60.0
margin = 20.0
scale = length/(end-start)
peaks = Drawing("SVGs/"+filename, size=(str(length) + "mm " , str(height)+"mm"), viewBox=("0 0 "+str(length+margin+20)+" "+str(height+margin+20)), preserveAspectRatio="xMinYMin meet")

heights = []
for pos, [height,stddev] in sorted(waves.iteritems()):
    print "Peak", pos, height, stddev
    X,Y=makegaussian(start, end, margin, length, pos,tail,offset,float(height), stddev)
    X = [round((x-offset+pos)*scale,3)+20 for x in X]
    for x in X:
        if x <(margin+0.05):
            X.insert(0,margin)
            Y.insert(0,tail)
            break
        if x >(margin+length-0.1):
            X.append(margin+length)
            Y.append(tail)
            break
    Y = [(40-y) for y in Y]
    #d is the list of coordinates with commands such as
    #M for "move to' to initiate curve and S for smooth curve
    d = "M"+str(X[0])+","+str(Y[0])+" "+str(X[1])+","+str(Y[1])
    for i in range(2,len(X)):
        d=d+(" "+str(X[i])+","+str(Y[i]))
    print "    " , d
    peaks.add(Path(stroke = color, stroke_width = 0.1, stroke_linecap = 'round', stroke_opacity = 0.8, fill = "slateblue",fill_opacity = 0.5, d = d))
    heights.append(height)


peaks.add(Text("Chipseq Peaks", insert = (margin,margin-10.0), fill="midnightblue", font_size = "5"))
xtics = [i for i in range(start,end) if i%1000==0]

for tic in xtics:
    tic_x = (margin+(tic-offset)*scale)
    tic_y = height + margin*2
    ticmarker=(Text(str(tic), insert = (tic_x,tic_y), fill="midnightblue", font_size = "3"))
    ticline = Rect(insert=(tic_x,height+margin*2-5-1 ), size = (0.1,2), fill="midnightblue")
    peaks.add(ticline)
    peaks.add(ticmarker)

#Add y tics
# ytics = [i for i in range(1, int(max(heights))) if i%4 ==0]
# ytics.append(0)
# for tic in ytics:
#     ticline = Rect(insert=(margin-5-1,margin-8+tic), size = (2,0.1), fill="midnightblue")
#     peaks.add(ticline)

x_axis = Rect(insert=(margin-5,height+margin*2-5), size = ((end-start)*scale+10,0.1), fill="midnightblue")
y_axis = Rect(insert=(margin-5,margin-8), size = (0.1,height+margin+3), fill="midnightblue")
peaks.add(x_axis)
peaks.add(y_axis)

peaks.save()




