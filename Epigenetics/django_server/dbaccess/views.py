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
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "common_utilities")
from MongoDB.mongoUtilities import MongoEpigeneticsWrapper
from MongoDB.mongoUtilities.common_utilities import CreateListFromCursor



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

    # print "q =", q

    p['organism'] = str(q.get("organism", "human"))
    p['collection'] = q.get("collection", "methylation")
    p['chipseq_project'] = []
    temp = q.getlist('chipseq', [])
    for t in temp:
        ti = t.split(",")
        for tj in ti:
            p['chipseq_project'].append(tj)
    p['methylation_project'] = []
    temp = q.getlist('methylation', [])
    for t in temp:
        ti = t.split(",")
        for tj in ti:
            p['methylation_project'].append(tj.encode('utf-8'))
    p['groupby_selected'] = q.get("groupby", None)
    p['chromosome'] = q.get("chromosome", None)
    p['minheight'] = q.get("minheight", None)
    p['minsigma'] = q.get("minsigma", None)
    p['tss'] = to_boolean(q.get("tss", False))
    p['cpg'] = to_boolean(q.get("cpg", False))
    p['show_dist'] = to_boolean(q.get("show_dist", False))
    p['datapoints'] = to_boolean(q.get("datapoints", True))
    p['sample_index'] = ast.literal_eval(str(q.get("sample_index", '{}')))
    p['types_index'] = ast.literal_eval(str(q.get("types_index", '{}')))
    p['width'] = int(q.get("width", 1000)) - 100    # width of screen minus 100
    p['height'] = int(q.get("height", 600)) - 300    # height of screen minus 300

    start = q.get("start", 0)
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

    if parameters['minheight'] is None:
        parameters['minheight'] = 0

    if parameters['minsigma'] is None:
        parameters['minsigma'] = 0

    db_list = [str(x) for x in mongo.database_names()]
    organism_list = []
    for f in db_list:
        if f.endswith("_epigenetics"):
            organism_list.append(f.replace("_epigenetics", ""))



    methylation_list = {}
    chipseq_list = {}
    groupby_list = {}
    for o in organism_list:
        proj_list = mongo[o + "_epigenetics"]['samples'].distinct("project")
        proj_list.sort()
        op_list = [str(x) for x in proj_list]
        methylation_list[o] = op_list
        chip_list = mongo[o + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False}).distinct('sample_id')
        chip_list.sort()
        cs_list = [x.encode('utf-8') for x in chip_list]
        chipseq_list[o] = cs_list

        gb = CreateListFromCursor(mongo[o + "_epigenetics"]['sample_groups'].find())
        byproj = {}
        for x in gb:
            a = x['available']
            if len(a) > 1:
                a = [y.encode('utf-8') for y in x['available']]
            else:
                a = x['available'][0].encode('utf-8')
            byproj[x['project'].encode('utf-8')] = {'default':x['default'].encode('utf-8'), 'available':a}
        groupby_list[o] = byproj





    # print "chipseq_list ", chipseq_list
    # print "chipseq:", parameters['chipseq']

    # variables:
    methylation, peaks = process_collection(parameters['collection'])

    if not methylation:
        parameters['methylation_project'] = None
    if not peaks:
        parameters['chipseq_project'] = None

    if methylation:
        if (len(parameters['methylation_project']) == 0) or (len(parameters['methylation_project']) > 1 or "All" in parameters['methylation_project']) :
            parameters['groupby_selected'] = 'project'
        elif parameters['methylation_project'][0] not in groupby_list[parameters['organism']]:
            parameters['groupby_selected'] = 'project'
        elif (parameters['groupby_selected'] is None and len(parameters['methylation_project']) == 1) :
            parameters['groupby_selected'] = groupby_list[parameters['organism']][parameters['methylation_project'][0]]['default']
        elif parameters['methylation_project'][0] not in methylation_list[parameters['organism']] :
            parameters['groupby_selected'] = groupby_list[parameters['organism']][parameters['methylation_project'][0]]['default']
        elif parameters['groupby_selected'] not in groupby_list[parameters['organism']][parameters['methylation_project'][0]]['available']:
            parameters['groupby_selected'] = groupby_list[parameters['organism']][parameters['methylation_project'][0]]['default']
        else:
            parameters['groupby_selected'] = parameters['groupby_selected'].encode('utf-8')
        print "Groupby Selected is now :", parameters['groupby_selected']


    database = parameters['organism'] + "_epigenetics"
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
                            height = parameters['height'],
                            width = parameters['width'],
                            get_tss = parameters['tss'],
                            get_cpg = parameters['cpg'],
                            sample_index = parameters['sample_index'],
                            show_points = parameters['datapoints'],
                            show_dist = parameters['show_dist'],
                            types_index = parameters['types_index'])

    return render(request, 'query_form.jade', {'organism_list':organism_list,
                                               'methylation_list':methylation_list,
                                               'collection_list':collection_list,
                                               'sample_index':sample_index,
                                               'types_index':types_index,
                                               'chipseq_list':chipseq_list,
                                               'chipseq_project':parameters['chipseq_project'],
                                               'plot':mark_safe(svg),
                                               'organism':parameters['organism'],
                                               'methylation_project':parameters['methylation_project'],
                                               'collection':parameters['collection'],
                                               'chromosome':parameters['chromosome'],
                                               'start':parameters['start'],
                                               'end':parameters['end'],
                                               'minheight':parameters['minheight'],
                                               'minsigma':parameters['minsigma'],
                                               'tss':parameters['tss'],
                                               'cpg':parameters['cpg'],
                                               'datapoints': parameters['datapoints'],
                                               'show_dist':parameters['show_dist'],
                                               'width':parameters['width'],
                                               'height':parameters['height'],
                                               'groupby':groupby_list,
                                               'groupby_selected':parameters['groupby_selected']}
                  )

