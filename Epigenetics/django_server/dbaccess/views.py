'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render


from pymongo.mongo_client import MongoClient
mongo = MongoClient('kruncher.cmmt.ubc.ca', 27017)

from viewtools import panning, zoom, check, query_all, query_chipseq, query_methylation

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
    ''' Instructions for parsing the query_form, and getting the names of the 
        information required to re-populate the drop down boxes and menus '''

    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST


    o = q.get("organism", "human")
    col = q.get("collection", "methylation")
    project = q.get('project', None)
    start = q.get("start", None)
    end = q.get("end", None)
    chrom = q.get("chromosome", None)
    action_factor = q.get("action", None)
    tss = q.get("tss", False)
    cpg = q.get("cpg", False)
    peaks = q.get("peaks", False)
    datapoints = q.get("datapoints", True)
    width = q.get("width", 1000)
    height = q.get("height", 600)

    if tss == 'on' or tss == 'true' or tss == True :
        tss = True
    else:
        tss = False
    if cpg == 'on' or cpg == 'true' or cpg == True:
        cpg = True
    else:
        cpg = False
    if datapoints == 'on' or datapoints == 'true' or datapoints == True:
        datapoints = True
    else:
        datapoints = False
    if peaks == 'on' or peaks == 'true' or peaks == True:
        peaks = True
    else:
        peaks = False

    if start is None or start == '' or start == True:
        start = 0
    elif start >= 0:
        start = int(start)
    else:
        start = 0

    if end is None or end == '' or end == True:
        end = start + 1
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

    if action_factor and (start >= 0) and (end >= 0):
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

    db_list = [str(x) for x in mongo.database_names()]
    organism_list = []
    for f in db_list:
        if f.endswith("_epigenetics"):
            organism_list.append(f.replace("_epigenetics", ""))
    print "default o: %s" % (o)

    proj_list = mongo[o + "_epigenetics"]['samples'].distinct("project")
    project_list = [str(x) for x in proj_list]
    project_list.sort()
    print "project_list ", project_list

    collection_list = {'chipseq':'ChIP-Seq', 'methylation':'Methylation', 'methchip':'Both'}

    parameters = {'organism':str(o), 'collection': str(col), 'project':project,
                  'chromosome': str(chrom), 'start': start, 'end':end,
                  'cpg':cpg, 'tss':tss, 'datapoints': datapoints, 'peaks':peaks,
                  'width':width, 'height':height }
    print 'parameters = ', parameters

    svg = 'Please query the database to generate an image!'
    if check(parameters):
        if col == 'methylation':
            svg = query_methylation(parameters)
        elif col == 'chipseq':
            svg = query_chipseq(parameters)
        elif col == 'methchip':
            svg = query_all(parameters)

    return render(request, 'query_form.jade', {'organism_list':organism_list, 'project_list':project_list,
                                               'collection_list':collection_list,
                                               'plot':mark_safe(svg), 'organism':o, 'project':project,
                                               'collection':col, 'chromosome':chrom, 'start':start,
                                               'end':end, 'tss':tss, 'cpg':cpg, 'datapoints': datapoints,
                                                'peaks':peaks, 'width':width, 'height':height})


