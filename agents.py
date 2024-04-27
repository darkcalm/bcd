from pyx import canvas, path, style

class DiagramAgent:
    def __init__(self, head, body):
        pass

class TextAgent:
    def __init__(self, interaction):
        pass

    def facilitates(self, agents):
        pass

class DrawAgent:
    def __init__(self, seed):
        
        def fetch_diagram(seed):
            return seed

        def fetch_filename(seed):
            return seed
            
        self.canvas = canvas.canvas()
        
        self.d = fetch_diagram(seed)
        self.f = fetch_filename(seed)

        self.conflicts = []
        self.evaluations = []
        
    def drawline_PyX(self, *args):
        self.canvas.stroke(path.line(*args), [style.linewidth.Thin])
    
    def drawtext_PyX(self, text_content, *xy): 
        self.canvas.text(*xy, text_content) # pkgs.texlive.combined.scheme-basic (nix)
    
    async def inspect(self):
        pass

    def evaluate(self):
        pass
    
    def inference(self):
        for e in self.evaluations:
            if e.type == 'line':
                self.drawline_PyX(self.canvas, *e.at[0], *e.at[1])
            elif e.type == 'text':
                self.drawtext_PyX(self.canvas, e.value, *e.at) 
        self.canvas.writeSVGfile(self.f)
    
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

