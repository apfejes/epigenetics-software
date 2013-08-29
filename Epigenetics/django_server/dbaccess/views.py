'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render

from pymongo import Connection
mongo = Connection('kruncher.cmmt.ubc.ca', 27017)

from viewtools import panning, zoom, check, query

def home_view(request):
    ''' TODO: fill in docstring '''
    return render(request, 'base.jade')

def view_collections(request):
    ''' TODO: fill in docstring '''
    db = mongo['human_epigenetics']
    collections = ""
    for item in db.collection_names():
        collections += item + ', '
    return render(request, 'collections.jade', {'collections':collections})

def send_svg(request):
    ''' TODO: fill in docstring '''
    from .Annotations import showgene
    return HttpResponse(showgene.svgcode())

def view_query_form(request):
    ''' TODO: fill in docstring '''
    svg = 'Try querying the database!'
    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    print "Q=", q

    o = q.get("organism", None)
    col = q.get("collection", None)
    start = q.get("start", None)
    end = q.get("end", None)
    chrom = q.get("chromosome", None)
    action_factor = q.get("action", None)
    tss = q.get("tss", False)
    cpg = q.get("cpg", False)
    peaks = q.get("peaks", False)
    width = q.get("width", 1000)
    height = q.get("height", 600)
    datapoints = q.get("datapoints", True)

    if action_factor and start and end:
        if 'Right' in action_factor or 'Left' in action_factor:
            print 'Action: panning!', action_factor
            start, end = panning(action_factor, int(start), int(end))
        elif 'In' in action_factor or 'Out' in action_factor:
            print 'Action: zooming!', action_factor
            start, end = zoom(action_factor, int(start), int(end))
        else:
            print 'Action not available:', action_factor
    else:
        print 'No action specified', action_factor

    print ("tss = ", tss)
    print ("peaks = ", peaks)

    if tss == 'on' or tss == 'true' or tss  :
        tss = True
    else:
        tss = False
    if cpg == 'on' or cpg == 'true' or cpg :
        cpg = True
    else:
        cpg = False
    if datapoints == 'on' or datapoints == 'true' or datapoints:
        datapoints = True
    else:
        datapoints = False
    if peaks == 'on' or peaks == 'true' or peaks:
        peaks = True
    else:
        peaks = False

    if start is None:
        pass
    elif start >= 0:
        start = int(start)
    else:
        start = 0

    if end is None:
        pass
    elif end > start:
        end = int(end)
    else:
        end = start + 1


    width = int(width) - 100
    if width < 600:
        width = 600

    height = int(height) - 300
    if height < 400:
        height = 400

    parameters = {'organism':str(o), 'collection': str(col),
                  'chromosome': str(chrom), 'start': start, 'end':end,
                  'cpg':cpg, 'tss':tss, 'datapoints': datapoints, 'peaks':peaks,
                  'width':width, 'height':height }
    print 'parameters = ', parameters

    if check(parameters):
        svg = query(parameters)
    return render(request, 'query_form.jade', {'plot':mark_safe(svg), 'organism':o,
                                               'collection':col, 'chromosome':chrom, 'start':start,
                                               'end':end, 'tss':tss, 'cpg':cpg, 'datapoints': datapoints,
                                                'peaks':peaks, 'width':width, 'height':height})
