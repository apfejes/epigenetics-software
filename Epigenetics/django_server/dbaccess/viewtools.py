'''
Created on 2013-08-23

@author: sperez

Tools used by views.py
'''

# Dictionary of zoom values
ZOOM_FACTORS = {'ZoomIn': 1.0 / 1.5, 'ZoomInMore': 1.0 / 3.0,
                'ZoomOut': 1.5, 'ZoomOutMore': 3.0}
# Dictionary of panning percentages from window that is shifted aside
PANNING_PERCENTS = {'LessRight':0.3, 'MoreRight':0.6,
               'LessLeft':-0.3, 'MoreLeft':-0.6}


def zoom(zoom_symbol, start, end):
    '''TODO: docstring missing'''

    # Adjusts start and end value for new query
    # ex: zoomfactor = 0.1, start = 200, end = 300
    span = (end - start)    # span of 100bp
    zoom_factor = ZOOM_FACTORS[zoom_symbol]
    new_span = span * zoom_factor    # span is now 10bp
    new_start = start + span / 2 - new_span / 2    # start is now 245
    new_end = end - span / 2 + new_span / 2    # end is now 255bp
    if new_start < 0:
        new_start = 0
    return int(new_start), int(new_end)



def panning(pan_factor, start, end):
    '''This code shifts the viewing window by the pan_factor.  Currently set above.'''
    # Adjusts start and end value for new query
    # ex: pan_factor = '>>', start = 200, end = 300
    start, end = int(start), int(end)
    percent = PANNING_PERCENTS[pan_factor]    # look up percent shift in dictionary
    shiftby = int((end - start) * percent)    # will be positive to go the right, negative to the left
    new_start = int(start + shiftby)
    new_end = int(end + shiftby)
    if new_start < 0:
        new_start = 0
    if new_end <= new_start:
        new_end = new_start + 1
    return new_start, new_end


def check(p):
    '''TODO: docstring missing'''
    if p['chromosome'] != 'None' and p['organism'] != 'None' and p['collection'] != 'None':
        return True
    else:
        return False

