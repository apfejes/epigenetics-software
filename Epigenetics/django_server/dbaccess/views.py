'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render


from pymongo.mongo_client import MongoClient
import os, sys
import ast

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(os.path.dirname(_cur_dir))
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoEpigeneticsWrapper
mongo = MongoClient('kruncher.cmmt.ubc.ca', 27017)


from viewtools import panning, zoom, check
collection_list = {'chipseq':'ChIP-Seq', 'methylation':'Methylation', 'methchip':'Both'}



def home_view(request):
    ''' a view for the home page, if required. '''
    return render(request, 'base.jade')

def view_collections(request):
    ''' Sample testing page to show the names of the collections in a mongo db.'''
    db = mongo['human_epigenetics']
    collections = ""
    for item in db.collection_names():
        collections += item + ', '
    return render(request, 'collections.jade', {'collections':collections})

def send_svg(request):
    ''' a page used for testing to display a piece of svg code.'''
    from .Annotations import showgene
    return HttpResponse(showgene.svgcode())

def to_boolean(value):
    '''test is value is true or false'''
    if value == 'on' or value == 'true' or value == True :
        return True
    else:
        return False


def process_collection(col):
    '''handle collection variable'''
    # shortcut for "both", but could be replaced later with this infrastructure

    peaks = False
    methylation = False

    if col == 'methchip':
        methylation = True
        peaks = True
        return methylation, peaks
    if col == 'methylation':
        methylation = True
        return methylation, peaks
    if col == 'chipseq':
        peaks = True
        return methylation, peaks
    print "  ---> Failed to recognize the type of graph requested: %s." % (col)
    return None

def process_request(request):
    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    p = {}    # parameters obtained

    print "q =", q

    p['organism'] = str(q.get("organism", "human"))
    p['collection'] = q.get("collection", "methylation")
    p['chipseq'] = q.get("chipseq", "All")    # list of chip seq samples available
    p['project'] = q.get('project', "All")
    p['chromosome'] = q.get("chromosome", None)
    p['tss'] = to_boolean(q.get("tss", False))
    p['cpg'] = to_boolean(q.get("cpg", False))
    p['show_dist'] = to_boolean(q.get("show_dist", False))
    p['datapoints'] = to_boolean(q.get("datapoints", True))
    p['sample_index'] = ast.literal_eval(str(q.get("sample_index", '{}')))
    p['types_index'] = ast.literal_eval(str(q.get("types_index", '{}')))
    p['width'] = int(q.get("width", 1000)) - 100    # width of screen minus 100
    p['height'] = int(q.get("height", 600)) - 300    # height of screen minus 300

    start = q.get("start", None)
    if start is None or start == '' or start == True:
        start = 0
    elif start >= 0:
        start = int(start)
    else:
        start = 0

    end = q.get("end", None)
    if end is None or end == '' or end == True:
        end = start + 1
    elif end > start:
        end = int(end)

    action_factor = q.get("action", None)    # don't save the "action factor" parameter.
    if action_factor and (start >= 0) and (end >= 0):
        if 'Right' in action_factor or 'Left' in action_factor:
            start, end = panning(action_factor, int(start), int(end))
        elif 'In' in action_factor or 'Out' in action_factor:
                start, end = zoom(action_factor, int(start), int(end))

    if end < start + 20:    # last chance to catch if you've zoomed in too far.
        end = start + 20

    p['start'] = start
    p['end'] = end

    return p



def view_query_form(request):
    ''' Instructions for parsing the query_form, and getting the names of the 
        information required to re-populate the drop down boxes and menus '''

    parameters = process_request(request)

    # adjust screen size if necessary.
    if parameters['width'] < 600:    # note proces_request already modifies these values from the window size passed in.
        parameters['width'] = 600

    if parameters['height'] < 400:
        parameters['height'] = 400

    db_list = [str(x) for x in mongo.database_names()]
    organism_list = []
    for f in db_list:
        if f.endswith("_epigenetics"):
            organism_list.append(f.replace("_epigenetics", ""))

    proj_list = mongo[parameters['organism'] + "_epigenetics"]['samples'].distinct("project")
    project_list = [str(x) for x in proj_list]
    project_list.append("All")
    project_list.append("Tissue")
    project_list.sort()
    print "project_list ", project_list
    print "project:", parameters['project']

    chip_list = mongo[parameters['organism'] + "_epigenetics"]['samples'].find({'haswaves': True}).distinct('chip')
    chipseq_list = [str(x) for x in chip_list]
    chipseq_list.append("All")
    chipseq_list.sort()
    print "chipseq_list ", chipseq_list
    print "chipseq:", parameters['chipseq']

    database = parameters['organism'] + "_epigenetics"

    # variables:
    methylation, peaks = process_collection(parameters['collection'])

    print("creating Mongo Wrapper on Database")

    m = MongoEpigeneticsWrapper.MongoEpigeneticsWrapper(database, methylation, peaks, parameters['start'], parameters['end'])

    svg = 'Please query the database to generate an image!'    # default string..  Should remove this.

    sample_index = {}
    types_index = {}

    print("Querying...")

    if check(parameters):
        if methylation and not peaks:
            docs = m.query(parameters)
            if parameters['tss'] or parameters['cpg']:
                m.getannotations(docs)
            svg, sample_index, types_index = m.svg_builder.svg(to_string = True,
                           title = "%s DNA methylation on %s (%i - %i)" %
                           (str.capitalize(parameters['organism']),
                               parameters['chromosome'],
                               parameters['start'], parameters['end']),
                           color = 'indigo',
                           height = parameters['height'],
                           width = parameters['width'],
                           get_tss = parameters['tss'],
                           get_cpg = parameters['cpg'],
                           show_points = parameters['datapoints'],
                           show_dist = parameters['show_dist'],
                           types_index = parameters['types_index'],
                           sample_index = parameters['sample_index'])


        elif peaks and not methylation:
            docs = m.query(parameters)
            if parameters['tss'] or parameters['cpg']:
                m.getannotations(docs)
            # print "DEBUG: parameters: ", parameters
            svg, sample_index, types_index = m.svg_builder.svg(to_string = True,
                            title = "%s Chip-Seq on %s (%i - %i)" %
                            (str.capitalize(parameters['organism']),
                               parameters['chromosome'],
                               parameters['start'], parameters['end']),
                            color = 'indigo',
                            height = parameters['height'],
                            width = parameters['width'],
                            get_tss = parameters['tss'],
                            get_cpg = parameters['cpg'],
                            types_index = parameters['types_index'],
                            sample_index = parameters['sample_index'])

        elif methylation and peaks:
            docs = m.query(parameters)
            if parameters['tss'] or parameters['cpg']:
                m.getannotations(docs)

            svg, sample_index, types_index = m.svg_builder.svg(to_string = True,
                            title = "%s DNA methylation and ChIP-Seq peaks on %s (%i - %i)" %
                            (str.capitalize(parameters['organism']),
                               parameters['chromosome'],
                               parameters['start'], parameters['end']),
                            color = 'indigo',
                            height = parameters['height'],
                            width = parameters['width'],
                            get_tss = parameters['tss'],
                            get_cpg = parameters['cpg'],
                            sample_index = parameters['sample_index'],
                            show_points = parameters['datapoints'],
                            show_dist = parameters['show_dist'],
                            types_index = parameters['types_index'])

    return render(request, 'query_form.jade', {'organism_list':organism_list, 'project_list':project_list,
                                               'collection_list':collection_list,
                                               'sample_index':sample_index,
                                               'types_index':types_index,
                                               'chip_list':chipseq_list,
                                               'chipseq':parameters['chipseq'],
                                               'plot':mark_safe(svg),
                                               'organism':parameters['organism'],
                                               'project':parameters['project'],
                                               'collection':parameters['collection'],
                                               'chromosome':parameters['chromosome'],
                                               'start':parameters['start'],
                                               'end':parameters['end'],
                                               'tss':parameters['tss'],
                                               'cpg':parameters['cpg'],
                                               'datapoints': parameters['datapoints'],
                                               'show_dist':parameters['show_dist'],
                                               'width':parameters['width'],
                                               'height':parameters['height']})

