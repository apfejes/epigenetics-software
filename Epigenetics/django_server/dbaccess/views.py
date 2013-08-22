'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.http import QueryDict
from django.utils.safestring import mark_safe
from django.shortcuts import render
from .queryforms import QueryForm
# from django.views.generic import TemplateView

from .Annotations import showmethylation, showchipseq

from pymongo import Connection
from django.core.context_processors import request
mongo = Connection('kruncher.cmmt.ubc.ca', 27017)

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
    form = None
    
    if request.method == 'GET':
        q = request.GET
        form = QueryForm(request.GET)    # A form bound to the POST data
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST
        form = QueryForm(request.POST)

    o = str(q.get("organism",None))
    col = str(q.get("collection",None))
    start = int(q.get("start",None))
    end = int(q.get("end",None))
    chrom = str(q.get("chromosome",None))
    
    parameters = {'organism':o, 'collection': col, 'chromosome':chrom, 'start':start, 'end':end}
    action_factor = q.get("action", None)
    
    if isinstance(action_factor, str):
        start,end = panning(action_factor, start, end)
    elif isinstance(action_factor, (int,long,float)):
        start,end = zoom(action_factor, start, end)
        
    print '\n\n',form
    #if form.is_valid():    # All validation rules pass
    #    svg = query(parameters)
    #else: 
    #    svg = "ERROR"
    if chech(parameters):
        svg = query(parameters)
    return render(request, 'query_form.jade', {'plot':mark_safe(svg), 'organism':o,
                                               'collection':col, 'chromosome':chrom, 'start':start,
                                               'end':end})

def check(p):
    if p['chromosome'] and p['organism'] and p['collection']:
        return True
    else:
        return False

def zoom(zoom_factor, start, end):
    # Adjusts start and end value for new query
    # ex: zoomfactor = 0.1, start = 200, end = 300
    span = (end - start)    # span of 100bp
    new_span = span * zoom_factor    # span is now 10bp
    new_start = span / 2 - new_span / 2    # start is now 245
    new_end = span / 2 + new_span / 2    # end is now 255bp
    return new_start, new_end

# Dictionary of panning percentages from window that is shifted aside
panning_percents = {'LessRight':0.6, 'MoreRight':0.9,
               'LessLeft':-0.6, 'MoreLeft':-0.9}

def panning(pan_factor, start, end):
    # Adjusts start and end value for new query
    # ex: pan_factor = '>>', start = 200, end = 300
    percent = panning_percents[pan_factor]    # look up percent shift in dictionary
    shiftby = (end - start) * percent    # will be positive to go the right, negative to the left
    return start + shiftby, end + shiftby

def parse_form(form):
    # Process the data in form.cleaned_data
    organism = str(form.cleaned_data['organism'])
    collection = str(form.cleaned_data['collection'])
    chromosome = 'chr' + str(form.cleaned_data['chromosome'])
    start = form.cleaned_data['start']
    end = form.cleaned_data['end']
#     if zoom_factor != 1:
#         start, end = zoom(zoom_factor, start, end)
#     if '>' or '<' in pan_factor:
#         start, end = panning(pan_factor, start, end)
    print "\n\n Received a form:", organism, collection, chromosome, start, end
    parameters = {'organism':organism, 'collection': collection, 'chromosome':chromosome, 'start':start, 'end':end}
    return  parameters

def query(p):
    if p['collection'] == 'chipseq':
        return showchipseq.svgcode(db = p['organism'], chromosome = p['chromosome'], start = p['start'], end = p['end'])
    elif p['collection'] == 'methylation':
        return showmethylation.svgcode(db = p['organism'], chromosome = p['chromosome'], start = p['start'], end = p['end'])
    else:
        return HttpResponse(p['collection'] + ' is an invalid collection! Please try again...')

