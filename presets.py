# bcd diagram bot presets are protocols that call modules with properties
# targets (seeds of text) are used to generate required properties
# requests are used to generate optional properties
# hashes: adler32

import re

def Payload(text, diagram=None, previous={}):
    try:        
        if diagram:
            return dict(
                dict(
                    {'diagram': Protocols[diagram], 'content': text},
                    **{'keyed': Protocols[diagram].seeded(previous)}
                ),
                **{'keyed': Protocols[diagram].seeded(text)}
            )
        
        text = [s.strip() for s in text.split('%', 1)]
        return dict(
            dict(
                {'diagram': Protocols[text[0]], 'content': text[1]},
                **{'keyed': Protocols[text[0]].seeded(previous)}
            ),
            **{'keyed': Protocols[text[0]].seeded(text[1])}
        )

    except KeyError:
        return None


class Diagram:
    def __init__(self, name="", keys={}, requests=[]):
        self.keys = keys
        self.requests = requests
    
    def printedseed(self, payload):
        return '%'.join([payload['diagram'],
                         ';'.join([re.escape(x) for x in payload['keyed']])])

    # tests: https://programiz.pro/ide/python/0B38DRB3MQ
    
    def seeded(self, text):
        try:
            return [
                {'key': k, 'quote': re.sub(r'\\(.)', r'\1', text.split(';')[i])}
                for i, k in enumerate(self.keys.keys())]
        except IndexError:
            return self.assigned(text)

    def assigned(self, text):
        return list(map(
            lambda x: {'key': x[0][0] or x[0][2],
                       'quote': [_[1] or _[3] for _ in x]},
            [x for x in [re.findall(
                r'^(1) ([^;]*)|; *(1) ([^;]*)[; ]*'.replace('1', k), text)
                         for k in self.keys.keys()
                        ] if x
            ]))


Protocols = {} 
Protocols['2x2'] = Diagram(
    name='twobytwo',
    keys={'q1': ['quadrant 1'], 'q2': ['quadrant 2'], 'q3': ['quadrant 3'], 'q4': ['quadrant 4'], 'xp': ['positive x'], 'xn': ['negative x'], 'yp': ['positive y'], 'yn': ['negative y'], 'x': ['axis x'], 'y': ['axis y'], 't': ['title']},
    requests={
        'functionandpropertiesandvalues1': ['line of x at xp/xn'],
        'functionandpropertiesandvalues2': ['line of y at yp/yn']
    })

Protocols['2of3'] = Diagram(
    name='twoofthree',
    keys={'u': ['top corner'], 'l': ['left corner'], 'r': ['right corner'], '-u': ['bottom side'], '-l': ['right side'], '-r': ['left side'], 't': ['title']},
    requests={
        'functionandproperties1': ['line of -u at l/r'],
        'functionandproperties2': ['line of -l at u/r'],
        'functionandproperties3': ['line of -r at u/l']
    })





'''
accepts={
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
}

accepts={
    'u': ['top corner', 'at polar(6,2) (0,1)'],
    'l': ['left corner', 'at polar(6,2) (2,1)'],
    'r': ['right corner', 'at polar(6,2) (4,1)'],
    '-u': ['bottom side', 'at middle(l,r)'],
    '-l': ['right side', 'at middle(u,r)'],
    '-r': ['left side', 'at middle(u,l)'],
    't': ['title', 'at cartesian(2,2) (-1,1)']
}
'''