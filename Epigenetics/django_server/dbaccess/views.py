'''
Created on 2013-05-07

@author: sperez, apfejes
'''


import ast, os, sys

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from mongoengine.queryset import DoesNotExist
from pymongo.mongo_client import MongoClient
import mongoengine

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(os.path.dirname(_cur_dir))
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "common_utilities")
from MongoDB.mongoUtilities import MongoEpigeneticsWrapper
from MongoDB.mongoUtilities.common_utilities import CreateListFromCursor
from viewtools import ZOOM_FACTORS, PANNING_PERCENTS, panning, zoom, check

sys.path.insert(0, _root_dir + os.sep + "django_server")
from django_server.settings import MONGO_HOST
from django_server.settings import MONGO_PORT
from django_server.settings import MONGO_SECURITY_DB


print "connecting to: %s %s %s" % (MONGO_SECURITY_DB, MONGO_HOST, MONGO_PORT)
mongo = MongoClient(MONGO_HOST, MONGO_PORT)    # general connection and library.
mongoengine.connect(MONGO_SECURITY_DB, host = MONGO_HOST, port = MONGO_PORT)    # security

collection_list = {'chipseq':'ChIP-Seq', 'methylation':'Methylation', 'methchip':'Both'}


def login_view(request):

    try:
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.get(username = username)
        # user.backend = 'mongoengine.django.auth.MongoEngineBackend'
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        authenticate(user = user, password = password)
        if not user.check_password(password):
            print "LOGIN --->  Incorrect password %s: " % (username)
            return render(request, 'base.jade', {"message":"Incorrect password provided for user %s" % (username)})
        if user.is_active:
            login(request, user)
            request.session.set_expiry(60 * 60 * 1)    # 1 hour timeout
            if next in request.POST:
                return HttpResponseRedirect(request.POST['next'])
            else:
                return render(request, 'base.jade', {"message":"Login successful"})
        else:    # Return a 'disabled account' error message
            print "LOGIN --->  Account for user %s has been deactivated." % (username)
            return render(request, 'base.jade', {"message":"Account for user %s has been deactivated." % (username)})
    except DoesNotExist:
        print "LOGIN --->  (Error:DoesNotExist) Could not authenticate user name %s: " % (username)
        return render(request, 'base.jade', {"message":"User %s does not exist." % (username)})
    except Exception as e:
        print "exeption", e
        return render(request, 'base.jade', {"message":"Unable to login.  Exception: %s" % (e)})


def logout_view(request):
    logout(request)
    return render(request, 'base.jade', {"message":"Log out successful"})

def loginpage(request):
    ''' a view for the home page, if required. '''
    if 'next' in request.POST:
        return render(request, 'loginpage.jade', {"next":request.POST['next']})
    else :
        return render(request, 'loginpage.jade')

def createuser(request):
    ''' a view for the home page, if required. '''
    User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
    return HttpResponse('user has been created')

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

def process_query_request(request):
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
    p['cpg'] = to_boolean(q.get("cpg", False))
    p['show_dist'] = to_boolean(q.get("show_dist", False))
    p['show_genes'] = to_boolean(q.get("show_genes", True))
    p['datapoints'] = to_boolean(q.get("datapoints", True))
    try:
        p['sample_index'] = request.session['sample_index']
        p['types_index'] = request.session['types_index']
    except KeyError:
        p['types_index'] = None
        p['sample_index'] = None
    # p['types_index'] = ast.literal_eval(str(q.get("types_index", '{}')))
    p['width'] = int(q.get("width", 1000)) - 200    # width of screen minus 100
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
        end = start + 10
    elif end > start:
        end = int(end)
    p['start'] = start
    p['end'] = end
    p['action_factor'] = q.get("action", None)    # don't need to save the "action factor" parameter, but need to check if it's a gene.
    return p


@login_required
def view_query_form(request):
    ''' Instructions for parsing the query_form, and getting the names of the 
        information required to re-populate the drop down boxes and menus '''


    parameters = process_query_request(request)

    # adjust screen size if necessary.
    if parameters['width'] < 600:    # note proces_request already modifies these values from the window size passed in.
        parameters['width'] = 600

    if parameters['height'] < 400:
        parameters['height'] = 400

    if parameters['minheight'] is None:
        parameters['minheight'] = 0

    if parameters['minsigma'] is None:
        parameters['minsigma'] = 0

    organism_list = [str(x).replace("_epigenetics", "") for x in mongo.database_names() if x.endswith("_epigenetics")]

    methylation_list = {}
    chipseq_list = {}
    groupby_list = {}
    for o in organism_list:
        proj_list = mongo[o + "_epigenetics"]['samples'].distinct("project")
        proj_list = [str(u) for u in proj_list if u is not None]
        proj_list.sort()
        methylation_list[o] = proj_list
        chip_list = mongo[o + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False}).distinct('sample_id')
        chip_list.sort()
        cs_list = [z.encode('utf-8') for z in chip_list]
        chipseq_list[o] = cs_list

        gb = CreateListFromCursor(mongo[o + "_epigenetics"]['sample_groups'].find())
        byproj = {}
        for x in gb:
            a = x['available']
            if len(a) > 1:
                a = [b.encode('utf-8') for b in x['available']]
            else:
                a = x['available'][0].encode('utf-8')
            byproj[x['project'].encode('utf-8')] = {'default':x['default'].encode('utf-8'), 'available':a}
        groupby_list[o] = byproj

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

    m = MongoEpigeneticsWrapper.MongoEpigeneticsWrapper(database, methylation, peaks)
    svg = 'Please query the database to generate an image!'    # default string..  Should remove this.

    action_factor = parameters.pop("action_factor")    # don't want to leave it in parameters.
    if action_factor in ZOOM_FACTORS:
        parameters['start'], parameters['end'] = zoom(action_factor, int(parameters['start']), int(parameters['end']))
    elif action_factor in PANNING_PERCENTS:
        parameters['start'], parameters['end'] = panning(action_factor, int(parameters['start']), int(parameters['end']))
    elif action_factor:
        coords = m.find_coords_by_gene(action_factor)
        if coords:
            parameters['chromosome'] = coords['chr']
            parameters['start'] = coords['start']
            parameters['end'] = coords['end']
        else:
            annotation = m.find_coords_by_probeid(action_factor)
            if annotation:
                parameters['chromosome'] = annotation['chr']
                parameters['start'] = annotation['mapinfo'] - 10
                parameters['end'] = annotation['mapinfo'] + 10
            else:
                return HttpResponse('Could not find Gene: ' + action_factor)

    if parameters['end'] < parameters['start'] + 10:    # must check this here, because placing the start and end too close together will 'cause x tics to fail.
        parameters['end'] = parameters['start'] + 10

    genes = []
    if parameters['show_genes']:
        genes = m.find_genes(str(parameters['chromosome']), parameters['start'], parameters['end'])

    sample_index = {}
    types_index = {}

    print("Querying...")

    if check(parameters):
        if methylation and not peaks:
            docs = m.query(parameters)
            if parameters['cpg']:
                m.getannotations(docs)
            svg, sample_index, types_index = m.svg_builder.svg(to_string = True,
                           title = "%s DNA methylation on %s (%i - %i)" %
                           (str.capitalize(parameters['organism']),
                               parameters['chromosome'],
                               parameters['start'], parameters['end']),
                           height = parameters['height'],
                           width = parameters['width'],
                           get_cpg = parameters['cpg'],
                           show_points = parameters['datapoints'],
                           show_dist = parameters['show_dist'],
                           show_genes = parameters['show_genes'],
                           types_index = parameters['types_index'],
                           sample_index = parameters['sample_index'],
                           genes = genes)


        elif peaks and not methylation:
            docs = m.query(parameters)
            if parameters['cpg']:
                m.getannotations(docs)
            # print "DEBUG: parameters: ", parameters
            svg, sample_index, types_index = m.svg_builder.svg(to_string = True,
                            title = "%s Chip-Seq on %s (%i - %i)" %
                            (str.capitalize(parameters['organism']),
                               parameters['chromosome'],
                               parameters['start'], parameters['end']),
                            height = parameters['height'],
                            width = parameters['width'],
                            get_cpg = parameters['cpg'],
                            types_index = parameters['types_index'],
                            sample_index = parameters['sample_index'],
                            genes = genes)

        elif methylation and peaks:
            docs = m.query(parameters)
            if parameters['cpg']:
                m.getannotations(docs)

            svg, sample_index, types_index = m.svg_builder.svg(to_string = True,
                            title = "%s DNA methylation and ChIP-Seq peaks on %s (%i - %i)" %
                            (str.capitalize(parameters['organism']),
                               parameters['chromosome'],
                               parameters['start'], parameters['end']),
                            height = parameters['height'],
                            width = parameters['width'],
                            get_cpg = parameters['cpg'],
                            sample_index = parameters['sample_index'],
                            show_points = parameters['datapoints'],
                            show_dist = parameters['show_dist'],
                            show_genes = parameters['show_genes'],
                            types_index = parameters['types_index'],
                            genes = genes)

    request.session['types_index'] = types_index
    request.session['sample_index'] = sample_index


    return render(request, 'query_form.jade', {'organism_list':organism_list,
                                               'methylation_list':methylation_list,
                                               'collection_list':collection_list,
                                               # 'sample_index':sample_index,
                                               # 'types_index':types_index,
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
                                               'cpg':parameters['cpg'],
                                               'datapoints': parameters['datapoints'],
                                               'show_dist':parameters['show_dist'],
                                               'show_genes':parameters['show_genes'],
                                               'width':parameters['width'],
                                               'height':parameters['height'],
                                               'groupby':groupby_list,
                                               'groupby_selected':parameters['groupby_selected'],
                                               'genes':genes}
                  )

@login_required
def view_metadata(request):
    organism_list = [str(x).replace("_epigenetics", "") for x in mongo.database_names() if x.endswith("_epigenetics") ]
    methylation_list = {}
    chipseq_list = {}
    for o in organism_list:
        proj_list = mongo[o + "_epigenetics"]['samples'].distinct("project")
        proj_list = [str(u) for u in proj_list if u is not None]
        proj_list.sort()
        methylation_list[o] = proj_list
        chip_list = mongo[o + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False}).distinct('sample_id')
        chip_list.sort()
        cs_list = [z.encode('utf-8') for z in chip_list]
        chipseq_list[o] = cs_list
    return render(request, 'metadata.jade', {"databases":organism_list,
                                             'collection_list':{'chipseq':'ChIP-Seq', 'methylation':'Methylation'},
                                             'methylation_list':methylation_list,
                                             'chipseq_list':chipseq_list})
@login_required
def view_metadata2(request):
    q = None
    if request.method == 'GET':
        return HttpResponseRedirect('/dbaccess/metadata/')
        # should not be using Get to submit to this page.
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    organism = str(q.get("organism", None))
    project = str(q.get("project", None))
    collection = str(q.get("collection", None))
    samples = None
    if collection == 'chipseq':
        samples = mongo[organism + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False, "sample_id":project})
        samples = [s for s in samples]
    elif collection == 'methylation':
        samples = []
        cursor = mongo[organism + "_epigenetics"]['samples'].find({'project':project})
        for s in cursor:
            for k in s:
                s[str(k)] = str(s.pop(k))
            samples.append(s)
    return render(request, 'metadata2.jade', {"organism":organism,
                                              "project":project,
                                              "samples":samples,
                                              "collection":collection})

@login_required
def view_metadata3(request):
    q = None
    if request.method == 'GET':
        return HttpResponseRedirect('/dbaccess/metadata/')
        # should not be using Get to submit to this page.
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST
    newfields = {}
    for t in q:
        if t.startswith("label"):
            v = t.replace("label", "value")
            newfields[str(q.get(t))] = str(q.get(v))
            # print "%s -> %s " % (q.get(t), q.get(v))

    organism = str(q.get("organism", None))
    project = str(q.get("project", None))
    collection = str(q.get("collection", None))
    sample = str(q.get("sample", None))

    print "collection = ", collection
    print "sample = ", sample
    print ("mongo[%s_epigenetics]['samples'].update({\"project\":\"%s\"},{$set:%s}") % (organism, project, newfields)

    if collection == "chipseq":
        print ("mongo[%s_epigenetics]['samples'].update({\"project\":\"%s\"},{$set:%s}") % (organism, project, newfields)
        # samples = mongo[organism + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False, "sample_id":project})
    elif collection == "methylation":
        print ("mongo[%s_epigenetics]['samples'].update({\"project\":\"%s\", \"sample\":%s},{$set:%s}") % (organism, project, sample, newfields)

    return render(request, 'metadata3.jade', {"type":collection})

    # if collection == 'chipseq':
    #    samples = mongo[organism + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False, "sample_id":project})
    #    samples = [s for s in samples]
    # elif collection == 'methylation':
    #    samples = []
    #    cursor = mongo[organism + "_epigenetics"]['samples'].find({'project':project})
    #    for s in cursor:
    #        for k in s:
    #            s[str(k)] = str(s.pop(k))
    #        samples.append(s)
