# bcd diagram bot presets are protocols that call modules with properties
# targets (seeds of text) are used to generate required properties
# requests are used to generate optional properties
# tests: https://programiz.pro/ide/python/0B38DRB3MQ

import re

from functools import reduce

# test https://programiz.pro/ide/python/0B38DRB3MQ

def Payload(*args):
    def flatten(dict_list):
        return {**dict_list[0], **flatten(dict_list[1:])}

    try:
        args = list(map(lambda x: (x[0][0].rstrip('%%').strip(),
                                   x[0][1].strip()),
                        [re.findall(r'(.*%%)*(.+)', t) for t in args]))

        P = Protocols[
        reduce(lambda a, b: a or b, [t[0] for t in args])]
        args = reduce(lambda a, b: {**a, **b}, [P.seeded(t[1]) if t[0] else P.assigned(t[1]) for t in args])

        return {'diagram': P, 'keyed': args}

    except KeyError:
        return None


class Diagram:
    def __init__(self, prefix, keys={}, seedformats={}, requests={}):
        self.prefix = prefix
        self.keys = keys
        self.seedformats = seedformats
        self.requests = requests

    def printedseed(self, keyed):
        return '%%'.join([
            self.prefix,
            ';'.join(
                [re.escape(keyed[k]['quote']) if k in keyed else '' for k in self.keys.keys()])])

    def descape(self, t):
        return re.sub(r'\\(.)', r'\1', t)

    def seeded(self, text):
        try:
            return dict(zip(
                [list(self.keys.keys())[i]
                 for i in self.seedformats[len(text.split(';'))]],
                list(map(
                    lambda t:{'quote': t},
                    [self.descape(t) for t in text.split(';')]))))

        except IndexError:
            return self.assigned(text)

    def assigned(self, text):
        def flatten(l):
            d = {}
            for m in l:
                if len(m) > 0:
                    d.update({
                        (m[-1][0] or m[-1][2]): {'quote':
                        self.descape(m[-1][1] or m[-1][3])}
                    })
            return d

        return flatten([re.findall(r'^(1) ([^;]*)|; *(1) ([^;]*)[; ]*'.replace('1', k), text) for k in self.keys.keys()])

Protocols = {} 
Protocols['2x2'] = Diagram(
    prefix='2x2',
    keys={'q1': ['quadrant 1'], 'q2': ['quadrant 2'], 'q3': ['quadrant 3'], 'q4': ['quadrant 4'], 'xp': ['positive x'], 'xn': ['negative x'], 'yp': ['positive y'], 'yn': ['negative y'], 'x': ['axis x'], 'y': ['axis y'], 't': ['title']},
    seedformats={11: list(range(11)), 10: list(range(10)), 8: list(range(8)), 6: list(range(4))+[8,9], 5: list(range(4))+[10], 4: list(range(4)), 2: [8,9], 1:[10]},
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