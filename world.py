class Diagram:
    def __init__(self, name="", meta={}, accepts={}, requests=[]):
        self.name = name
        self.meta = meta
        self.accepts = accepts
        self.requests = requests

places = {}
places['955e7e81b6120cad67ce9890b9d18276'] = Diagram(
    name='twobytwo', meta={'scale': 1}, accepts={
    'q1': ['quadrant 1', 'at cartesian(4,4) (1,1)'],
    'q2': ['quadrant 2', 'at cartesian(4,4) (-1,1)'],
    'q3': ['quadrant 3', 'at cartesian(4,4) (-1,-1)'],
    'q4': ['quadrant 4', 'at cartesian(4,4) (1,-1)'],
    'xp': ['positive x', 'at cartesian(4,4) (2,0)'],
    'xn': ['negative x', 'at cartesian(4,4) (-2,0)'],
    'yp': ['positive y', 'at cartesian(4,4) (0,2)'],
    'yn': ['negative y', 'at cartesian(4,4) (0,-2)'],
    'x': ['axis x', 'at cartesian(4,4) (1,0)'],
    'y': ['axis y', 'at cartesian(4,4) (0,1)'],
    't': ['title', 'at cartesian(4,4) (-2,2)']
}, requests=['line of x communicates xp/xn', 'line of y communicates yp/yn'])

places['2d203aaff5b2a70c5a24fab8c26a0095'] = Diagram(
    name='twoofthree', meta={'scale': 1, 'special': '/'}, accepts={
    'u': ['top corner', 'at polar(6,2) (0,1)'],
    'l': ['left corner', 'at polar(6,2) (2,1)'],
    'r': ['right corner', 'at polar(6,2) (4,1)'],
    '-u': ['bottom side', 'at middle(l,r)'],
    '-l': ['right side', 'at middle(u,r)'],
    '-r': ['left side', 'at middle(u,l)'],
    't': ['title', 'at cartesian(2,2) (-1,1)']
}, requests=['line of -u communicates l/r', 'line of -l communicates u/r', 'line of -r communicates u/l'])