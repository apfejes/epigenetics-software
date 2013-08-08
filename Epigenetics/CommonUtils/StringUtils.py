'''
Common string utilties.

Created on 2013-08-07

@author: afejes
'''

def rreplace(s, old, new, occurrence):
    ''' Nice implementation via http://stackoverflow.com/questions/2556108/
    how-to-replace-the-last-occurence-of-an-expression-in-a-string'''
    li = s.rsplit(old, occurrence)
    return new.join(li)





if __name__ == '__main__':
    pass