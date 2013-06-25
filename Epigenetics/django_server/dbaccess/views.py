'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from queryforms import QueryForm
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
    return render(request, 'collections.jade')

def view_query_form(request):
    return render(request, 'query_form.jade')

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
    from Annotations import showmethylation
    string = showmethylation.svgcode()
    return HttpResponse(string)

def chipseq_code(request, chr, start, end):
    from Annotations import showchipseq
    string = showchipseq.svgcode(chr = chr, start = start, end = end)
    return HttpResponse(string)

def send_svg(request):
    from Annotations import showgene
    return HttpResponse(showgene.svgcode())

def query(request):
    if request.method == 'POST': # If the query has been submitted...
        form = QueryForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            collection = str(form.cleaned_data['collection'])
            chr = 'chr' + str(form.cleaned_data['chr'])
            start = str(form.cleaned_data['start'])
            end = str(form.cleaned_data['end'])
            print collection, chr, start, end
            if collection == 'chipseq':
                return chipseq_code(request, chr, start, end)
            elif collection == 'methylation':
                return HttpResponse('The \'' + collection + '\' collection is not available yet.')
            else: 
                return HttpResponse(collection + ' is an invalid collection! Please try again...')
        else:
            return HttpResponse('You query parameters were invalid! Please try again...') # Redirect after POST
    else:
        #form = QueryForm() # An unbound form
        return HttpResponse('You query parameters were invalid! Please try again...') # Redirect after POS

