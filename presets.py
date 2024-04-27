# bcd diagram bot presets are protocols that call modules with properties
# targets (seeds of text) are used to generate required properties
# requests are used to generate optional properties
# hashes: https://www.md5hashgenerator.com/
class Diagram:
    def __init__(self, name="", uses={}, options={}, othertargets=[], resolutions=[]):
        self.name = name
        self.uses = uses
        self.options = options
        self.othertargets = othertargets
        self.conflictresolutions = resolutions

Protocols = {}
Protocols['6a59fb8cc78202203894ba8de45c70ed'] = Diagram(
    name='twobytwo',
    uses={0: 'hashofmodule', 'optionstarget': 'functionandproperty'},
    options={'q1': ['quadrant 1'], 'q2': ['quadrant 2'], 'q3': ['quadrant 3'], 'q4': ['quadrant 4'], 'xp': ['positive x'], 'xn': ['negative x'], 'yp': ['positive y'], 'yn': ['negative y'], 'x': ['axis x'], 'y': ['axis y'], 't': ['title']},
    othertargets={
        'functionandpropertiesandvalues1': ['line of x at xp/xn'],
        'functionandpropertiesandvalues2': ['line of y at yp/yn']
    })

Protocols['c11f9788a863907937ae9889ca57eed3'] = Diagram(
    name='twoofthree',
    uses={0: 'hashofmodule', 'optionstarget': 'functionandproperty'},
    options={'u': ['top corner'], 'l': ['left corner'], 'r': ['right corner'], '-u': ['bottom side'], '-l': ['right side'], '-r': ['left side'], 't': ['title']},
    othertargets={
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