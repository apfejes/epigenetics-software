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
    return render(request, 'base.jade')

def view_collections(request):
    db = mongo['human_epigenetics']
    collections = ""
    for item in db.collection_names():
        collections += item + ', '
    return render(request, 'collections.jade', {'collections':collections})

def send_svg(request):
    from .Annotations import showgene
    return HttpResponse(showgene.svgcode())

def view_query_form(request):
    svg = 'Try querying the database!'
    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    o = q.get("organism", None)
    col = q.get("collection", None)
    start = q.get("start", None)
    end = q.get("end", None)
    chrom = q.get("chromosome", None)
    action_factor = q.get("action", None)
    tss = q.get("tss", False)
    cpg = q.get("cpg", False)
    

    if action_factor and start and end:
        if 'Right' in action_factor or 'Left' in action_factor:
            print 'panning!', action_factor
            start,end = panning(action_factor, int(start), int(end))
        elif 'In' in action_factor or 'Out' in action_factor:
            print 'zooming!', action_factor
            start,end = zoom(action_factor, int(start), int(end))
        else:
            print 'Action not available:', action_factor
    else: 
        print 'No action specified', action_factor

    if tss:
        print tss
        tss = True
    if cpg:
        print cpg
        cpg = True
    if start:
        start = int(start)
    if end:
        end = int(end)

    parameters = {'organism':str(o), 'collection': str(col), 'chromosome': str(chrom), 'start': start, 'end':end, 'cpg':cpg, 'tss':tss}
    print parameters

    if check(parameters):
        svg = query(parameters)
    return render(request, 'query_form.jade', {'plot':mark_safe(svg), 'organism':o,
                                               'collection':col, 'chromosome':chrom, 'start':start,
                                               'end':end, 'tss':tss, 'cpg':cpg})
