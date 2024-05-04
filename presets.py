# bcd diagram bot presets are protocols that call modules with properties
# tests: https://programiz.pro/ide/python/0B38DRB3MQ

import re

from functools import reduce

def Payload(*args):
    try:
        args = list(map(lambda x: (x[0][0].rstrip('<>').strip(), x[0][1].strip()), [re.findall(r'(.*<>)*(.+)', arg) for arg in args]))

        P = Protocols[reduce(lambda a, b: a or b, [arg[0] for arg in args])]
        
        args = reduce(lambda a, b: {**a, **b}, [P.assignedbyseed(arg[1]) if arg[0] else P.assignedbykey(arg[1]) for arg in args])

        return {'diagram': P, 'keyed': args}

    except KeyError:
        return None

class Diagram:
    def __init__(self, prefix, keys={}, seedformats={}, requests={}):
        self.prefix = prefix
        self.keys = keys
        self.seedformats = seedformats # should be seedgenerator
        self.requests = requests

    def printedseed(self, keyed):
        return ' <> '.join([
            self.prefix,
            '; '.join(
                [re.escape(keyed[k]['assigned']) if k in keyed else '' for k in self.keys.keys()])])

    def descape(self, t):
        return re.sub(r'\\(.)', r'\1', t)

    def seedformatgenerator(self):
        return

    def assignedbyseed(self, text):
        try:
            return dict(zip(
                [list(self.keys.keys())[i]
                 for i in self.seedformats[len(text.split(';'))]],#reaching for seedformat should be a whole function
                list(map(
                    lambda t: {'assigned': t},
                    [self.descape(t) for t in text.split(';')]))))

        except IndexError:
            return self.assignedbykey(text)

    def assignedbykey(self, text):
        def flatten(l):
            return { (m[-1][0] or m[-1][2]): {'assigned': self.descape(m[-1][1] or m[-1][3])} for m in l if len(m) > 0 }

        return flatten([re.findall(r'^(1) ([^;]*)|; *(1) ([^;]*)[; ]*'.replace('1', k), text) for k in self.keys.keys()])

Protocols = {} 
Protocols['2x2'] = Diagram(
    prefix='2x2',
    keys={'q1': ['quadrant 1'], 'q2': ['quadrant 2'], 'q3': ['quadrant 3'], 'q4': ['quadrant 4'], 'xp': ['positive x'], 'xn': ['negative x'], 'yp': ['positive y'], 'yn': ['negative y'], 'x': ['axis x'], 'y': ['axis y'], 't': ['title']},
    seedformats={11: list(range(11)), 10: list(range(10)), 9: list(range(8))+[10], 8: list(range(8)), 7: list(range(4,11)), 6: list(range(4,10)), 5: list(range(4,8))+[10], 4: list(range(4,8)), 3:[8,9,10], 2: [8,9], 1:[10]},
    requests={
        'functionandpropertiesandvalues1': ['line of x at xp/xn'],
        'functionandpropertiesandvalues2': ['line of y at yp/yn']
    })

Protocols['2/3'] = Diagram(
    prefix='2/3',
    keys={'u': ['top corner'], 'l': ['left corner'], 'r': ['right corner'], '-u': ['bottom side'], '-l': ['right side'], '-r': ['left side'], 't': ['title']},
    seedformats={7: list(range(7)), 6: list(range(6)), 4: list(range(3))+[6], 3: list(range(3)), 1:[7]},
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