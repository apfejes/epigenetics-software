# Create your views here.

'''
Created on 2013-05-07

@author: sperez
'''


from django.http import HttpResponse
from django.shortcuts import render

#from django.views.generic import TemplateView


#Code for using MongoDB.mongoUttilities.MongoConnector

#import sys
#import os
#_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
#_root_dir = os.path.dirname(_cur_dir)
#sys.path.insert(0, _root_dir)
#sys.path.insert(0, _cur_dir)
#sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
#import Mongo_Connector
#mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)



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


def collections(request):
	db= mongo[database_name]
	return db.collection_names()
#	return HttpResponse(db.collection_names())

def view_svg(request):
	with open("dbaccess/Annotations/SVGs/gene.svg","rb") as f:
		return HttpResponse(f.read(), mimetype = "image/svg+xml")
	
def send_svg(request):
	from Annotations import showgene
	return HttpResponse(showgene.svgcode())

