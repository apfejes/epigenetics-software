

from numpy import log
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import sqrt, exp

#replace
#waves to self. waves
#start to self. start

waves = {36993: [13.33, 72], 29250: [12.54, 19], 29573: [15.8, 25], 37153: [18.52, 79], 29489: [26.22, 38], 28712: [18.43, 79]}
filename = "peaks.svg"
smooth = True
color = "indigo"

def makegaussian(pos,offset,height, stddev):
    X=[]
    tail =int((sqrt((-2)*stddev*stddev*log(1/height))))
    for i in range (-stddev,stddev,1):
        X.append(float(i))
    for i in range (-tail, -stddev,5):
        X.append(float(i))
    for i in range (stddev,tail,5):
        X.append(float(i))
    if (tail) not in X: X.append(tail)
    X.sort()
    X = [float(x) for x in X]
    X = [x for x in X if (x+pos-offset)>=0]
    stddev = float(stddev)
    Y = [round(height*exp(-x*x/(2*stddev*stddev)),2) for x in X]
    return X,Y
start = 28800
offset = start
end = 38000
length = int((start - end)/100+20)
height  =  20
gene = Drawing("SVGs/"+filename, size=(str(length) + "mm " , str(height)+"mm"), viewBox=("0 0 "+str(length+10)+" "+str(height+20)), preserveAspectRatio="xMinYMin meet")

for pos, [height,stddev] in sorted(waves.iteritems()):
    print pos, height, stddev
    X,Y=makegaussian(pos,offset,height, stddev)
    X = [round((x-offset+pos)/100,3)+20 for x in X]
    for x in X:
        if x <20.10:
            X.insert(0,20)
            Y.insert(0,1)
            break
    #do same for right tails
    Y = [(40-y) for y in Y]
    #d is the list of coordinates with commands such as
    #M for "move to' to initiate curve and S for smooth curve
    d = "M"+str(X[0])+","+str(Y[0])+" "+str(X[1])+","+str(Y[1])
    for i in range(2,len(X)):
        d=d+(" "+str(X[i])+","+str(Y[i]))
    print d
    gene.add(Path(stroke = color, stroke_width = 0.1, stroke_linecap = 'round', stroke_opacity = 0.8, fill = "slateblue",fill_opacity = 0.5, d = d))
gene.save()