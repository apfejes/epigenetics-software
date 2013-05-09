# Create your views here.

'''
Created on 2013-05-07

@author: sperez
'''


from django.http import HttpResponse

import sys
import os

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector


database_name = 'human_epigenetics'
annotation_collection = 'annotations'
methylation_collection = 'methylation'
sample_collection = 'samples'

mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)

def index(request):
	introduction  = "Hello world! Welcome to the Human Epigenetics database. \n This page tests the connection to our Mongo database."
	#pull data from the epigenetics database
		
	return HttpResponse(introduction)