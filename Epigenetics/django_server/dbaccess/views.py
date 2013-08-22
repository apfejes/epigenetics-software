'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render
from .queryforms import QueryForm
# from django.views.generic import TemplateView

from .Annotations import showmethylation, showchipseq

from pymongo import Connection
mongo = Connection('kruncher.cmmt.ubc.ca', 27017)

def home_view(request):
    return render(request, 'base.jade')

def view_collections(request):
    db = mongo[database_name]
    collections = ""
    for item in db.collection_names():
        collections += item + ', '
    return render(request, 'collections.jade', {'collections':collections})

def chipseq_code(database, chromosome, start, end):
    string = showchipseq.svgcode(db = database, chromosome = chromosome, start = start, end = end)
    return HttpResponse(string)

def meth_code(database, chromosome, start, end):
    string = showmethylation.svgcode(db = database, chromosome = chromosome, start = start, end = end)
    return string

def send_svg(request):
    from .Annotations import showgene
    return HttpResponse(showgene.svgcode())

def view_query_form(request):
    svg = 'Try querying the database!'
    if request.method == 'POST':    # If the query has been submitted...
        form = QueryForm(request.POST)    # A form bound to the POST data
        if form.is_valid():    # All validation rules pass
            svg = query(parse_form(form))
        else:
            return HttpResponse('You query parameters were invalid! Please try again...')    # Redirect after POST
    return render(request, 'query_form.jade', {'plot':mark_safe(svg)} )

def zoom(zoom_factor,start,end):
    return start,end

def parse_form(form):
    # Process the data in form.cleaned_data
    database = str(form.cleaned_data['database'])
    collection = str(form.cleaned_data['collection'])
    chromosome = 'chr' + str(form.cleaned_data['chromosome'])
    zoom_factor = int(form.cleaned_data['zoom'])
    start = form.cleaned_data['start']
    end = form.cleaned_data['end']
    if zoom_factor != 1:
        start, end = zoom(zoom_factor,start, end)
    print "\n\n Received a form:", database, collection, chromosome, start, end
    return  database, collection, chromosome, start, end

def query(database, collection, chromosome, start, end):
    if collection == 'chipseq':
        return showchipseq.svgcode(db = database, chromosome = chromosome, start = start, end = end)
    elif collection == 'methylation':
        return showmethylation.svgcode(db = database, chromosome = chromosome, start = start, end = end)
    else:
        return HttpResponse(collection + ' is an invalid collection! Please try again...')

