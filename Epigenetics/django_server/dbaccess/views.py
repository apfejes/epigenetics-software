'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render
# from django.views.generic import TemplateView

from .Annotations import showmethylation, showchipseq

from pymongo import Connection
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

    if start:
        start = int(start)
    if end:
        end = int(end)
    parameters = {'organism':str(o), 'collection': str(col), 'chromosome': str(chrom), 'start': start, 'end':end}
    print parameters

    if check(parameters):
        svg = query(parameters)
    return render(request, 'query_form.jade', {'plot':mark_safe(svg), 'organism':o,
                                               'collection':col, 'chromosome':chrom, 'start':start,
                                               'end':end})

def check(p):
    if p['chromosome'] != 'None' and p['organism'] != 'None' and p['collection'] != 'None':
        return True
    else:
        return False

def zoom(zoom_symbol, start, end):
    # Adjusts start and end value for new query
    # ex: zoomfactor = 0.1, start = 200, end = 300
    span = (end - start)    # span of 100bp
    zoom_factor = zoom_factors[zoom_symbol]
    new_span = span * zoom_factor    # span is now 10bp
    new_start = start + span / 2 - new_span / 2    # start is now 245
    new_end = end - span / 2 + new_span / 2    # end is now 255bp
    print 'span', span, 'factor', zoom_factor, 'new', new_span
    print start,end, 'are now', new_start, new_end
    return int(new_start), int(new_end)

# Dictionary of panning percentages from window that is shifted aside
panning_percents = {'LessRight':0.6, 'MoreRight':0.9,
               'LessLeft':-0.6, 'MoreLeft':-0.9}

zoom_factors = {'ZoomIn': 0.33, 'ZoomInMore': 0.1,
                'ZoomOut': 3, 'ZoomOutMore': 10}

def panning(pan_factor, start, end):
    # Adjusts start and end value for new query
    # ex: pan_factor = '>>', start = 200, end = 300
    start, end = int(start), int(end)
    percent = panning_percents[pan_factor]    # look up percent shift in dictionary
    print pan_factor, percent
    shiftby = int((end - start) * percent)    # will be positive to go the right, negative to the left
    print shiftby
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
    length = 260.0
    width = 80.0
    margin = 20.0
    if p['collection'] == 'chipseq':
        return showchipseq.svgcode(db = p['organism'], 
                                   chromosome = p['chromosome'], 
                                   start = p['start'], 
                                   end = p['end'],
                                   length = length,
                                   width = width,
                                   margin = margin)
    elif p['collection'] == 'methylation':
        return showmethylation.svgcode(db = p['organism'], 
                                   chromosome = p['chromosome'], 
                                   start = p['start'], 
                                   end = p['end'],
                                   length = length,
                                   width = width,
                                   margin = margin)
    else:
        return HttpResponse(p['collection'] + ' is an invalid collection! Please try again...')

