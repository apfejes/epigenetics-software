'''
Created on 2013-05-07

@author: sperez
'''
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.shortcuts import render


from pymongo.mongo_client import MongoClient
import os, sys
import json

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(os.path.dirname(_cur_dir))
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
from MongoDB.mongoUtilities import MongoEpigeneticsWrapper
import Annotations.showchipseq as showchipseq
import Annotations.showchipandmeth as showchipandmeth
mongo = MongoClient('kruncher.cmmt.ubc.ca', 27017)


from viewtools import panning, zoom, check
collection_list = {'chipseq':'ChIP-Seq', 'methylation':'Methylation', 'methchip':'Both'}



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

def to_boolean(value):
    '''test is value is true or false'''
    if value == 'on' or value == 'true' or value == True :
        return True
    else:
        return False


def process_collection(col):
    '''handle collection variable'''
    # shortcut for "both", but could be replaced later with this infrastructure
    if col == 'methchip':
        methylation = True
        peaks = True
        return methylation, peaks

    if col == 'methylation':
        methylation = True
    else:
        methylation = False

    if col == 'chipseq':
        peaks = True
    else:
        peaks = False
    return methylation, peaks



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
    show_dist = q.get("show_dist", False)
    datapoints = q.get("datapoints", True)
    sample_index = q.get("samples", None)
    types_index = q.get("types", None)
    width = q.get("width", 1000)
    height = q.get("height", 600)

    tss = to_boolean(tss)
    cpg = to_boolean(cpg)
    datapoints = to_boolean(datapoints)
    show_dist = to_boolean(show_dist)

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
    project_list.append("All")
    project_list.append("Tissue")
    project_list.sort()
    print "project_list ", project_list



    database = o + "_epigenetics"

    # variables:
    methylation, peaks = process_collection(col)

    print("creating Mongo Wrapper on Database")

    m = MongoEpigeneticsWrapper.MongoEpigeneticsWrapper(database, methylation, peaks, start, end)


    parameters = {'organism':str(o), 'collection': str(col),
                  'chromosome': str(chrom), 'start': start, 'end':end,
                  'cpg':cpg, 'tss':tss, 'datapoints': datapoints, 'show_dist':show_dist,
                  'width':width, 'height':height }
    if project != "All" and project != "Tissue":
        parameters['project'] = str(project)
    else:
        parameters['project'] = None
    print 'parameters = ', parameters


    svg = 'Please query the database to generate an image!'
    print "sample_index = %s" % (sample_index)
#     if sample_index:
#         sample_index = json.loads(sample_index)
#     if types_index:
#         types_index = json.loads(types_index)



    if check(parameters):
        if methylation and not peaks:
            svg, sample_index, types_index = svg_methylation_code(m,
                                   methylation,
                                   peaks,
                                   json.dumps(sample_index),
                                   json.dumps(types_index),
                                   organism = str.capitalize(parameters['organism']),
                                   project = parameters['project'],
                                   chromosome = parameters['chromosome'],
                                   start = parameters['start'],
                                   end = parameters['end'],
                                   height = parameters['height'],
                                   width = parameters['width'],
                                   tss = parameters['tss'],
                                   cpg = parameters['cpg'],
                                   datapoints = parameters['datapoints'],
                                   show_dist = parameters['show_dist'])
        elif peaks and not methylation:
            svg, sample_index = showchipseq.svgcode(m, sample_index,
                               organism = str.capitalize(parameters['organism']),
                               chromosome = parameters['chromosome'],
                               start = parameters['start'],
                               end = parameters['end'],
                               height = parameters['height'],
                               width = parameters['width'],
                               tss = parameters['tss'],
                               cpg = parameters['cpg'])


        elif methylation and peaks:
            svg = showchipandmeth.svgcode(m, sample_index,
                                organism = str.capitalize(parameters['organism']),
                                project = parameters['project'],
                                chromosome = parameters['chromosome'],
                                start = parameters['start'],
                                end = parameters['end'],
                                height = parameters['height'],
                                width = parameters['width'],
                                tss = parameters['tss'],
                                cpg = parameters['cpg'],
                                datapoints = parameters['datapoints'],
                                show_dist = parameters['show_dist'])

    return render(request, 'query_form.jade', {'organism_list':organism_list, 'project_list':project_list,
                                               'collection_list':collection_list, 'sample_index':sample_index,
                                               'types_index':types_index,
                                               'plot':mark_safe(svg), 'organism':o, 'project':project,
                                               'collection':col, 'chromosome':chrom, 'start':start,
                                               'end':end, 'tss':tss, 'cpg':cpg, 'datapoints': datapoints,
                                               'show_dist':show_dist, 'width':width, 'height':height})



def svg_methylation_code(mongowrapper,
                         methylation,
                         peaks,
                         sample_index,
                         types_index,
                         organism = None,
                         project = None,
                         chromosome = None,
                         start = None,
                         end = None,
                         height = None,
                         width = None,
                         tss = False,
                         cpg = False,
                         datapoints = False,
                         show_dist = False):
    '''TODO:missing docstring'''

    print("Querying...")
    docs = mongowrapper.query(methylation = methylation,
                              peaks = peaks,
                              project = project,
                              chromosome = chromosome,
                              start = start,
                              end = end)
    if tss or cpg:
        mongowrapper.getannotations(docs)
    if chromosome[0:3] != 'chr':
        chromosome = 'chr' + str(chromosome)
    return mongowrapper.svg_builder.svg(to_string = True,
                           title = organism + " DNA methylation on " + chromosome + " (" + str(start) + "-" + str(end) + ")",
                           color = 'indigo',
                           height = height,
                           width = width,
                           get_tss = tss,
                           get_cpg = cpg,
                           show_points = datapoints,
                           show_dist = show_dist,
                           types_index = types_index,
                           sample_index = sample_index)

