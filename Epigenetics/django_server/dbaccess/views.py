'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.shortcuts import render
from .queryforms import QueryForm
# from django.views.generic import TemplateView


database_name = 'human_epigenetics'
annotation_collection = 'annotations'
methylation_collection = 'methylation'
sample_collection = 'samples'

from pymongo import Connection
mongo = Connection('kruncher.cmmt.ubc.ca', 27017)

def my_view(request):
    return render(request, 'base.jade')

def view_collections(request):
    db = mongo[database_name]
    collections = ""
    for item in db.collection_names():
        collections += item + ', '
    return render(request, 'collections.jade', {'collections':collections})

def view_methylation(request):
    return render(request, 'methylation.jade')

def view_chipseq(request):
    return render(request, 'chipseq.jade')

def collections(request):
    db = mongo[database_name]
    # return db.collection_names()
    x = " "
    for item in db.collection_names():
        x += item + '\n\n  '
    return HttpResponse(x)

def methylation_code(request):
    from .Annotations import showmethylation
    string = showmethylation.svgcode()
    return string

def chipseq_code(request, database, chromosome, start, end):
    from .Annotations import showchipseq
    string = showchipseq.svgcode(db = database, chromosome = chromosome, start = start, end = end)
    return HttpResponse(string)

def meth_code(request, database, chromosome, start, end):
    from .Annotations import showmethylation
    string = showmethylation.svgcode(db = database, chromosome = chromosome, start = start, end = end)
    return HttpResponse(string)

def send_svg(request):
    from .Annotations import showgene
    return HttpResponse(showgene.svgcode())

def view_query_form(request):
    print 'query_form'
    svg = ''
    if request.method == 'POST':    # If the query has been submitted...
        svg = query(request)
    print svg
    return render(request, 'query_form.jade')

def query(request):
    print 'query'
    if request.method == 'POST':    # If the query has been submitted...
        form = QueryForm(request.POST)    # A form bound to the POST data
        if form.is_valid():    # All validation rules pass
            # Process the data in form.cleaned_data
            database = str(form.cleaned_data['database'])
            collection = str(form.cleaned_data['collection'])
            chromosome = 'chr' + str(form.cleaned_data['chromosome'])
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            print "\n\n Received a form:", database, collection, chromosome, start, end
            if collection == 'chipseq':
                return chipseq_code(request, database, chromosome, start, end)
            elif collection == 'methylation':
                return meth_code(request, database, chromosome, start, end)
                # return HttpResponse('The \'' + collection + '\' collection is not available yet.')
            else:
                return HttpResponse(collection + ' is an invalid collection! Please try again...')
        else:
            return HttpResponse('You query parameters were invalid! Please try again...')    # Redirect after POST
    else: 
        print 'try'
        return HttpResponse('Try querying the database!')

