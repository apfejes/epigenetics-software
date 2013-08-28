'''
Created on 2013-08-23

@author: sperez

Tools used by views.py
'''
from .Annotations import showmethylation, showchipseq, showchipandmeth

# Dictionary of zoom values
zoom_factors = {'ZoomIn': 1.0 / 1.5, 'ZoomInMore': 1.0 / 3.0,
                'ZoomOut': 1.5, 'ZoomOutMore': 3.0}

def zoom(zoom_symbol, start, end):
    '''TODO: docstring missing'''

    # Adjusts start and end value for new query
    # ex: zoomfactor = 0.1, start = 200, end = 300
    span = (end - start)    # span of 100bp
    zoom_factor = zoom_factors[zoom_symbol]
    new_span = span * zoom_factor    # span is now 10bp
    new_start = start + span / 2 - new_span / 2    # start is now 245
    new_end = end - span / 2 + new_span / 2    # end is now 255bp
    return int(new_start), int(new_end)

# Dictionary of panning percentages from window that is shifted aside
panning_percents = {'LessRight':0.6, 'MoreRight':0.9,
               'LessLeft':-0.6, 'MoreLeft':-0.9}

def panning(pan_factor, start, end):
    '''TODO: docstring missing'''
    # Adjusts start and end value for new query
    # ex: pan_factor = '>>', start = 200, end = 300
    start, end = int(start), int(end)
    percent = panning_percents[pan_factor]    # look up percent shift in dictionary
    shiftby = int((end - start) * percent)    # will be positive to go the right, negative to the left
    return start + shiftby, end + shiftby


def check(p):
    '''TODO: docstring missing'''
    if p['chromosome'] != 'None' and p['organism'] != 'None' and p['collection'] != 'None':
        return True
    else:
        return False

def query(p):
    '''TODO: docstring missing'''
    if p['collection'] == 'chipseq':
        return showchipseq.svgcode(db = p['organism'],
                                   chromosome = p['chromosome'],
                                   start = p['start'],
                                   end = p['end'],
                                   height = p['height'],
                                   width = p['width'],
                                   tss = p['tss'],
                                   cpg = p['cpg'])
    elif p['collection'] == 'methylation':
        return showmethylation.svgcode(db = p['organism'],
                                   chromosome = p['chromosome'],
                                   start = p['start'],
                                   end = p['end'],
                                   height = p['height'],
                                   width = p['width'],
                                   tss = p['tss'],
                                   cpg = p['cpg'],
                                   datapoints = p['datapoints'],
                                   peaks = p['peaks'])
    elif p['collection'] == 'methchip':
        return showchipandmeth.svgcode(db = p['organism'],
                                   chromosome = p['chromosome'],
                                   start = p['start'],
                                   end = p['end'],
                                   height = p['height'],
                                   width = p['width'],
                                   tss = p['tss'],
                                   cpg = p['cpg'],
                                   datapoints = p['datapoints'],
                                   peaks = p['peaks'])
    else:
        return p['collection'] + ' is an invalid collection! Please try again...'
