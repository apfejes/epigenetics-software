'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.shortcuts import render

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

def view_methylation(request):
	return render(request, 'methylation.jade')

def view_chipseq(request):
	return render(request, 'chipseq.jade')

def collections(request):
	db = mongo[database_name]
# 	return db.collection_names()
	x = " "
	for item in db.collection_names():
		x += item + '\n\n  '
	return HttpResponse(x)

def methylation_code(request):
	from Annotations import showmethylation
	string = showmethylation.svgcode()
	return HttpResponse(string)

def chipseq_code(request):
	from Annotations import showchipseq
	string = showchipseq.svgcode()
	return HttpResponse(string)

def send_svg(request):
	from Annotations import showgene
	return HttpResponse(showgene.svgcode())


