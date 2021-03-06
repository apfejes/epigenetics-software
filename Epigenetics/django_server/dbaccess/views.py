'''
Created on 2013-05-07

@author: sperez, apfejes
'''


import os, sys, io, time

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from bson.objectid import ObjectId

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
    '''This function processes the results from the login screen.  It uses the django authentication
    functions to process the login/password, and verify it against the database.'''

    try:
        print "request Method = ", request.method

        if request.method == 'GET':
            q = request.GET
        elif request.method == 'POST':
            q = request.POST

        n = q['next']
        print "next = ", n

        username = q['username']    # from dialog boxes
        password = q['password']
        user = User.objects.get(username = username)    # create a user object
        # user.backend = 'mongoengine.django.auth.MongoEngineBackend'
        user.backend = 'django.contrib.auth.backends.ModelBackend'    # this backend interacts with the database to interpret passwords
        authenticate(user = user, password = password)    # this command verifies that the password is correct
        print "made it this far"
        if not user.check_password(password):
            print "LOGIN --->  Incorrect password %s: " % (username)
            return render(request, 'base.jade', {"message":"Incorrect password provided for user %s" % (username)})
        print "made it this far 2"
        if user.is_active:    # users must be active to proceed
            login(request, user)    # create the login workings.
            request.session.set_expiry(60 * 60 * 1)    # 1 hour timeout
            if n:
                print "made it this far 3"
                return HttpResponseRedirect(n)
            else:
                return render(request, 'base.jade', {"message":"Login successful"})


        else:    # Return a 'disabled account' error message
            print "made it this far 5"
            print "LOGIN --->  Account for user %s has been deactivated." % (username)    # account exists, but has been locked.
            return render(request, 'base.jade', {"message":"Account for user %s has been deactivated." % (username)})
    except DoesNotExist:    # no user.
        print "LOGIN --->  (Error:DoesNotExist) Could not authenticate user name %s: " % (username)
        return render(request, 'base.jade', {"message":"User %s does not exist." % (username)})
    except Exception as e:    # any other error
        print "exception", e
        return render(request, 'base.jade', {"message":"Unable to login.  Exception: %s" % (e)})


def logout_view(request):
    logout(request)
    return render(request, 'base.jade', {"message":"Log out successful"})

def loginpage(request):
    ''' a view for the home page, if required. '''
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':
        q = request.POST

    if 'next' in q:
        print "request.GET['next']= ", q['next']
        return render(request, 'loginpage.jade', {"next":q['next']})

    return render(request, 'loginpage.jade', {"next":None})

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
    p = {}    # parameters obtained
    if request.method == 'GET':
        q = request.GET
        f = q.get("filters", [])
        if "," in f:
            print "splitting"
            f = f.split(",")
            p['show_groups'] = [x.encode('utf-8') for x in f]
        else:
            p['show_groups'] = []
            if f:
                p['show_groups'].append(f)

    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST
        p['show_groups'] = []
        for key in q:    # process fields with variable names
            if key.startswith("filter_"):
                p['show_groups'].append(key.replace("filter_", "").encode('utf-8'))

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
    p['trace'] = to_boolean(q.get("trace", False))
    p['cpg'] = to_boolean(q.get("cpg", False))
    p['show_dist'] = to_boolean(q.get("show_dist", False))
    p['show_genes'] = to_boolean(q.get("show_genes", False))
    p['datapoints'] = to_boolean(q.get("datapoints", False))
    p['bigger_dists'] = to_boolean(q.get("bigdist", False))
    try:
        p['sample_index'] = request.session['sample_index']
        p['types_index'] = request.session['types_index']
    except KeyError:
        p['types_index'] = None
        p['sample_index'] = None
    p['width'] = int(q.get("width", 900)) - 300    # width of screen minus 100
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

    p['genename'] = q.get("genename", None)

    if not q.get("organism", None):    # set some defaults:
        p['show_genes'] = True
        p['datapoints'] = True


    return p


@login_required
def view_query_form(request):
    ''' Instructions for parsing the query_form, and getting the names of the 
        information required to re-populate the drop down boxes and menus 
        Tag @login_required indicates that the security should be verified before proceeding.'''

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

    # each database must be named XXXX_epigenetics, where XXXX is the name of the organism.
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
            if len(a) > 0:
                a = [b.encode('utf-8') for b in x['available']]
            c = []
            if 'compound' in x:
                c = x['compound'].keys()
                if len(c) > 0:
                    c = [b.encode('utf-8') for b in c]
            a.extend(c)
            if len(a) == 1:
                a = a[0].encode('utf-8')
            byproj[x['project'].encode('utf-8')] = {'default':x['default'].encode('utf-8'), 'available':a}
        groupby_list[o] = byproj

    methylation, peaks = process_collection(parameters['collection'])    # check whether to include methylation or chip-seq or both.

    if not methylation:
        parameters['methylation_project'] = None
    if not peaks:
        parameters['chipseq_project'] = None

    if methylation:
        if (len(parameters['methylation_project']) == 0):
            parameters['groupby_selected'] = 'project'
        elif len(parameters['methylation_project']) > 1:
            pass
            # print "parameters['groupby_selected'] = ", parameters['groupby_selected']
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

    database = parameters['organism'] + "_epigenetics"
    # print("creating Mongo Wrapper on Database")

    m = MongoEpigeneticsWrapper.MongoEpigeneticsWrapper(database, methylation, peaks)
    svg = '<br><br><br><br><h2 style="margin-left:100px; text-align:center;">Please select parameters from the options on the right<br> to query the database and generate an image!</h2>'


    action_factor = parameters.pop("action_factor")    # don't want to leave it in parameters.
    if action_factor in ZOOM_FACTORS:
        parameters['start'], parameters['end'] = zoom(action_factor, int(parameters['start']), int(parameters['end']))
    elif action_factor in PANNING_PERCENTS:
        parameters['start'], parameters['end'] = panning(action_factor, int(parameters['start']), int(parameters['end']))
    elif parameters['genename']:    # check to see if a gene/probe name has been entered
        coords = m.find_coords_by_gene(parameters['genename'])
        if coords:
            parameters['chromosome'] = coords['chr']
            parameters['start'] = coords['start']
            parameters['end'] = coords['end']
        else:
            annotation = m.find_coords_by_probeid(parameters['genename'])
            if annotation:
                parameters['chromosome'] = annotation['chr']
                parameters['start'] = annotation['mapinfo'] - 100
                parameters['end'] = annotation['mapinfo'] + 100
            else:
                return HttpResponse('Could not find Gene: ' + parameters['genename'])

    if parameters['chromosome'] == "":
        print "no chromosome specified - setting to chr1"
        parameters['chromosome'] = "chr1"

    if parameters['end'] < parameters['start'] + 10:    # must check this here, because placing the start and end too close together will 'cause x tics to fail.
        parameters['end'] = parameters['start'] + 10

    genes = []
    if parameters['show_genes']:    # this gets the information for showing genes on the SVG illustration.
        genes = m.find_genes(str(parameters['chromosome']), parameters['start'], parameters['end'])

    sample_index = {}
    types_index = {}

    if check(parameters):
        if methylation and not peaks:    # if only showing methylation
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
                           show_groups = parameters['show_groups'],
                           bigger_dists = parameters['bigger_dists'],
                           trace = parameters['trace'],
                           genes = genes)


        elif peaks and not methylation:    # if only showing chipseq
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
                            trace = parameters['trace'],
                            genes = genes)

        elif methylation and peaks:    # if showing both
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
                            show_groups = parameters['show_groups'],
                            bigger_dists = parameters['bigger_dists'],
                            trace = parameters['trace'],
                            genes = genes)

    for key in reversed(parameters['show_groups']):    # must traverse backwards, otherwise removing keys causes elements to be skipped.
        if key not in types_index:
            parameters['show_groups'].remove(key)

    request.session['show_groups'] = sorted(parameters['show_groups'])    # session information is cookies.
    request.session['types_index'] = types_index
    request.session['sample_index'] = sample_index


    return render(request, 'query_form.jade', {'organism_list':organism_list,    # create the web page
                                               'methylation_list':methylation_list,
                                               'collection_list':collection_list,
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
                                               'bigdist':parameters['bigger_dists'],
                                               'trace':parameters['trace'],
                                               'genes':genes}
                  )

@login_required
def view_metadata(request):
    '''create a web page that allows you to pick a collection to modify.'''
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
    '''edit the meta data for a given project'''
    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    # print "q =", q
    organism = str(q.get("organism", None))
    project = str(q.get("project", None))
    collection = str(q.get("collection", None))
    samples = None
    groups = None
    if collection == 'chipseq':
        samples = mongo[organism + "_epigenetics"]['samples'].find({'haswaves': True, 'hide': False, "sample_id":project})
        samples = [s for s in samples]
    elif collection == 'methylation':
        samples = []
        groups = []
        cursor = mongo[organism + "_epigenetics"]['samples'].find({'project':project})
        for s in cursor:
            for k in s:
                s[str(k)] = str(s.pop(k)).replace("'", "")
            samples.append(s)
        cursor = mongo[organism + "_epigenetics"]['sample_groups'].find({'project':project})
        for s in cursor:
            t = s['available']
            for k in t:
                groups.append(str(k))

    return render(request, 'metadata2.jade', {"organism":organism,
                                              "project":project,
                                              "samples":samples,
                                              "groups":groups,
                                              "collection":collection})

@login_required
def view_metadata3(request):
    q = None

    if request.method == 'GET':    # should not be using Get to submit to this page.
        return HttpResponseRedirect('/dbaccess/metadata/')

    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    organism = str(q.get("organism", None))
    project = str(q.get("project", None))
    collection = str(q.get("collection", None))
    sampleoid = str(q.get("sampleoid", None))

    newfields = {}
    updated_groups = []
    for t in q:
        if t.startswith("label"):
            newfields[str(t)] = str(q.get(t))
        if t.startswith("checkbox_"):
            v = t.replace("checkbox_", "")
            updated_groups.append(v)

    mongo[organism + "_epigenetics"]['sample_groups'].update({"project":project}, {"$set":{"available":updated_groups}}, upsert = True)

    one = mongo[organism + "_epigenetics"]['sample_groups'].find({"project":project, "default":{ "$exists": True}}).count()
    if one < 1:
        mongo[organism + "_epigenetics"]['sample_groups'].update({"project":project}, {"$set":{"default":updated_groups[0]}})

    if sampleoid:
        mongo[organism + "_epigenetics"]['samples'].update({"project":project, "_id":ObjectId(sampleoid)}, {"$set":newfields}, upsert = False)
        print " ran -> mongo[%s_epigenetics]['samples'].update({\"project\":%s, \"_id\":%s}, {\"$set\":%s}, upsert = False)" % (organism, project, ObjectId(sampleoid), newfields)

    return render(request, 'metadata3.jade', {"type":collection})


@login_required
def delete_sample(request):

    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    soid = q.get("sampleoid", None)
    organism = q.get("organism", None)
    confirm = q.get("confirm", None)
    c = mongo[organism + "_epigenetics"]['samples'].find_one({"_id":ObjectId(soid)})
    project = c['project']
    sampleid = c['sampleid']

    print "Confirm = ", confirm

    if not confirm:
        return render(request, 'delete_sample.jade', {"sampleoid":soid,
                                                  "organism":organism,
                                                  "project":project,
                                                  "sampleid":sampleid})
    else:
        print "removing methylation data for %s from project %s" % (sampleid, project)
        mongo[organism + "_epigenetics"]['methylation'].update({"project":project}, {"$unset":{"b." + str(sampleid):1}}, multi = True)
        print "done"
        print "removing sample %s from project %s" % (sampleid, project)
        mongo[organism + "_epigenetics"]['samples'].remove({"_id":ObjectId(soid)})
        return render(request, 'deleted.jade', {"message":
             "Sample %s in project %s has been deleted from the %s_epigenetics database." % (sampleid, project, organism)})



@login_required
def delete_project(request):

    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST


    organism = q.get("organism", None)
    confirm = q.get("confirm", None)
    project = q['project']
    if not confirm:
        return render(request, 'delete_project.jade', {"organism":organism,
                                                  "project":project})
    else:
        print "removing methylation data for project %s" % (project)
        mongo[organism + "_epigenetics"]['methylation'].remove({"project":project}, multi = True)
        print "done"
        print "removing samples from project %s" % (project)
        mongo[organism + "_epigenetics"]['samples'].remove({"project":project}, multi = True)
        print "removing sample_groups for project %s" % (project)
        mongo[organism + "_epigenetics"]['sample_groups'].remove({"project":project}, multi = True)
        return render(request, 'deleted.jade', {"message":
             "Project '%s' has been deleted from the %s_epigenetics database." % (project, organism)})




@login_required
def compound(request):
    ''''Generates the page for creating compound "group by" keys.'''

    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    project = str(q.get("project", None))
    organism = str(q.get("organism", None))

    if "delete" in q:
        name = str(q.get("delete"))
        value = mongo[organism + "_epigenetics"]['sample_groups'].update({"project":project}, {"$unset":{"compound." + name: ""}})
        print value
    elif "key1" in q and "key2" in q and "key3" in q:
        key1 = str(q.get("key1"))
        key2 = str(q.get("key2"))
        if key1 != "None" and key2 != "None":
            key3 = str(q.get("key3"))
            name = str(q.get("name"))
            if key3 == "None":
                value = mongo[organism + "_epigenetics"]['sample_groups'].update({"project":project}, {"$set":{"compound." + name: [key1, key2]}})
                print value
            else:
                value = mongo[organism + "_epigenetics"]['sample_groups'].update({"project":project}, {"$set":{"compound." + name: [key1, key2, key3]}})
                print value
    cursor = mongo[organism + "_epigenetics"]['sample_groups'].find({'project':project})

    groups = []
    groupby = []

    for s in cursor:
        t = s['available']
        for k in t:
            groups.append(str(k))
        if "compound" in s:
            groupby.append(s['compound'])

    return render(request, 'compound.jade', {"project":project,
                                             "organism":organism,
                                             "groups":groups,
                                             "groupby":groupby})

@login_required()
def import_metadata(request):

    '''create a web page that allows you to pick a collection to modify.'''
    organism_list = [str(x).replace("_epigenetics", "") for x in mongo.database_names() if x.endswith("_epigenetics") ]
    return render(request, 'import.jade', {"databases":organism_list,
                                             'collection_list':{'methylation':'Methylation'}})
@login_required()
def import_files(request):
    q = None
    if request.method == 'GET':
        q = request.GET
    elif request.method == 'POST':    # If the query has been submitted...
        q = request.POST

    organism = q.get("organism", None)
    return render(request, 'import2.jade', {"organism":organism})

def convert_number(x):
    if x.isdigit():
        x = int(x)
    else:
        try:
            x = float(x)
        except ValueError:
            pass
    return x


@login_required()
def import_process(request):
    time0 = time.time()
    if request.method != "POST":
        return render(request, 'base.jade', {"message":"The page you were attempting to view should only be arrived at via a POST query.  Something has gone wrong."})
    organism = str(request.POST.get("organism", None))
    project = str(request.POST.get("project", None))


    if not ('sampleFile' in request.FILES) or not ('betaFile' in request.FILES):
	return render(request, 'base.jade', {"message":"One or more file selections were missing.  Please go back and try again."})


    print "organism = ", organism
    print "project = ", project
    first = True
    headers = []
    sampleIdCol = 0;
    to_insert = []
    samples = 0
    for line in io.StringIO(unicode(request.FILES['sampleFile'].read()), newline = None):
        insertrow = {}
        if first:    # header row
            headers = [str(col) for col in line.replace("\n", "").split("\t")]
            print "headers ", headers
            if 'Sample_ID' in headers:
                sampleIdCol = headers.index('Sample_ID')
                headers[sampleIdCol] = "sampleid"
            first = False
        else:
            data = line.replace("\n", "").split("\t")
            data = [str(d) for d in data]
            for i, x in enumerate(data):
                x = str(x)
                if i == sampleIdCol:
                    insertrow[headers[i]] = str(x).replace(".", "_")
                    continue
                else:
                    insertrow[headers[i]] = convert_number(x)
            insertrow['project'] = project
            print "insertrows = ", insertrow
            to_insert.append(insertrow)
            samples += 1

        if len(to_insert) > 0 and samples % 10000 == 0:
            mongo[organism + "_epigenetics"]['samples'].insert(to_insert)
            to_insert = []

    if to_insert:
        mongo[organism + "_epigenetics"]['samples'].insert(to_insert)
    print "%i samples processed" % samples


    methylation = 0
    first = True
    to_insert = []
    for line in io.StringIO(unicode(request.FILES['betaFile'].read()), newline = None):
        insertrow = {}
        if first:    # header row
            headers = [str(col).replace(".AVG_Beta", "").replace(".", "_") for col in line.replace("\n", "").split("\t")][1:]
            print "headers ", headers
            first = False
        else:
            data = line.replace("\n", "").split("\t")
            data = [str(d) for d in line.split("\t")][1:]
            insertrow['pid'] = data[0]
            insertrow['project'] = project
            insertrow['b'] = {}
            for d in range(1, len(data)):
                try:
                    insertrow['b'][headers[d]] = float(data[d])
                except ValueError:
                    continue
            # print "insertrows = ", insertrow
            to_insert.append(insertrow)
            methylation += 1

        if len(to_insert) > 0 and methylation % 10000 == 0:
            mongo[organism + "_epigenetics"]['methylation'].insert(to_insert)
            to_insert = []
            render(request, 'base.jade', {"message":"processed " + str(methylation) + " rows"})

    if to_insert:
        mongo[organism + "_epigenetics"]['methylation'].insert(to_insert)
    print "%i methylation probes processed" % methylation

    time1 = time.time()

    return render(request, 'import3.jade', {"project":project, "samples":samples,
                           "methylrows":methylation, "timetaken":round(time1 - time0, 1)})

