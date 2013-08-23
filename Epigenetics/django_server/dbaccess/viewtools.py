'''
Created on 2013-08-23

@author: sperez

Tools used by views.py
'''
from .Annotations import showmethylation, showchipseq
from django.http import HttpResponse

LENGTH = 260.0
WIDTH = 80.0
MARGIN = 20.0

#Dictionary of zoom values
zoom_factors = {'ZoomIn': 1/1.5, 'ZoomInMore': 1/3,
                'ZoomOut': 1.5, 'ZoomOutMore': 3.0}

def zoom(zoom_symbol, start, end):
    # Adjusts start and end value for new query
    # ex: zoomfactor = 0.1, start = 200, end = 300
    span = (end - start)    # span of 100bp
    zoom_factor = zoom_factors[zoom_symbol]
    new_span = span * zoom_factor    # span is now 10bp
    new_start = start + span / 2 - new_span / 2    # start is now 245
    new_end = end - span / 2 + new_span / 2    # end is now 255bp
    print 'span', span, 'factor', zoom_factor, 'new', new_span
    print start,end, 'are now', new_start, new_end
    return int(new_start), int(new_end)

# Dictionary of panning percentages from window that is shifted aside
panning_percents = {'LessRight':0.6, 'MoreRight':0.9,
               'LessLeft':-0.6, 'MoreLeft':-0.9}

def panning(pan_factor, start, end):
    # Adjusts start and end value for new query
    # ex: pan_factor = '>>', start = 200, end = 300
    start, end = int(start), int(end)
    percent = panning_percents[pan_factor]    # look up percent shift in dictionary
    print pan_factor, percent
    shiftby = int((end - start) * percent)    # will be positive to go the right, negative to the left
    print shiftby
    return start + shiftby, end + shiftby


def check(p):
    if p['chromosome'] != 'None' and p['organism'] != 'None' and p['collection'] != 'None':
        return True
    else:
        return False

def query(p):
    if p['collection'] == 'chipseq':
        return showchipseq.svgcode(db = p['organism'], 
                                   chromosome = p['chromosome'], 
                                   start = p['start'], 
                                   end = p['end'],
                                   LENGTH = LENGTH,
                                   WIDTH = WIDTH,
                                   MARGIN = MARGIN)
    elif p['collection'] == 'methylation':
        return showmethylation.svgcode(db = p['organism'], 
                                   chromosome = p['chromosome'], 
                                   start = p['start'], 
                                   end = p['end'],
                                   LENGTH = LENGTH,
                                   WIDTH = WIDTH,
                                   MARGIN = MARGIN)
    else:
        return HttpResponse(p['collection'] + ' is an invalid collection! Please try again...')
