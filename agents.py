from pyx import canvas, path

class OptionAgent:
    def __init__(self, head, body):
        pass

class TextAgent:
    
    def __init__(self, interaction, diagram):
        self.seed = ""
        self.diagram = diagram

        self.agents = [OptionAgent(k, v) for k, v in self.diagram.options.items()]
        self.conflicts = {'overlaps': []} # should populate by diagram
        self.evaluations = {}

    def inspects(self):
        pass
            
    def facilitates(self):
        pass

    def infers(self, previous):
        pass

class DrawAgent:
    def __init__(self, key, text):
        pass

class DrawAgents:
    def __init__(self, diagram, seed):
        self.canvas = canvas.canvas()
        self.diagram = diagram
    
        self.agents = [DrawAgent(key, text) for key, text in zip(self.diagram.options.keys(), seed) if text] # should include lines
        self.conflicts = {'overflows': [self.agents], 'overlaps': [self.agents], 'nones': [self.agents]}
        self.evaluations = {}
    
    def __line__(self, *args):
        self.canvas.stroke(path.line(*args))

    def __text__(self, *args): 
        self.canvas.text(*args) # pkgs.texlive.combined.scheme-basic (nix)

    def __inspecttext__(self, *args):
        pass
    
    def __inspectline__(self, *args):
        pass


    def inspects(self):
        for a in self.agents:
            # run agents to inspect things
            pass
    
    def facilitates(self, conflictagents):
        pass
    
    def infers(self):
        # assign agent values to m and arg
        for m, args in self.evaluations.items():
            eval(m)(*args)
        return self.canvas.writeSVGfile(self.diagram.name)

'''

import re
from functools import reduce
from operator import iconcat

def texts_to_query(text, agent):
    tf = [q.strip(' ') for q in re.split(r"(?<!\\)"+self.delimiter, tf)]

    if len(tf) == len(diagram.get_agents()):
        return [(a.key, tf[i]) for i, a in enumerate(diagram.get_agents())]

    return [(q.split(' ', 1)[0], q.split(' ', 1)[1:]) for q in tf if (len(q.split(' ', 1)) > 1) and (q.split(' ', 1)[0] in diagram.get_agent_keys())]

def amend_querys(query):
    return {k:v for (k, v) in reduce(iconcat, query, [])}

def query_to_seed(query):
    return self.delimiter.join([(query[k] if k in query else '')
                           for k in diagram.get_agent_keys()])

texts = [texts] if isinstance(texts, str) else texts

return query_to_seed(
    amend_querys(
        [texts_to_query(tf) for tf in texts]
    )
)
'''

