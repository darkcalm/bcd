import re

from functools import reduce
from operator import iconcat


from wand.api import library
import wand.color
import wand.image

from pyx import *


class DiagramAction:
    def __init__(self, at=None, plan=None, draw=None):
        self.requestdata = {}
        self.executedata = {}
        self.memorydata = {}
        

class Epoch:
    def __init__(self, delimiter):
        self.delimiter = delimiter

    async def texts_to_seeds(self, texts, diagram):
    
        def texts_to_query(tf):
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
    
    
    async def seeds_to_files(self, seeds, filename):
    
        c = canvas.canvas()
    
        def drawline_PyX(c, *args):
            c.stroke(path.line(*args), [style.linewidth.Thin])
    
        # text requires pkgs.texlive.combined.scheme-basic (nix)
        def drawtext_PyX(c, text_content, *xy):
            c.text(*xy, text_content)
    
        for r in requests:
            if r.type == 'line':
                drawline_PyX(c, *r.at[0], *r.at[1])
            elif r.type == 'text':
                drawtext_PyX(c, r.value, *r.at)
    
        c.writeSVGfile(filename)
    
        with wand.image.Image(resolution = 300) as image:
            with wand.color.Color('white') as background_color:
                library.MagickSetBackgroundColor(image.wand, 
                                                 background_color.resource) 
            image.read(blob=open(filename+'.svg', "r").read().encode('utf-8'), format="svg")
            png_image = image.make_blob("png32")
        with open(filename+'.png', "wb") as out:
            out.write(png_image)
    
        files = []
        for extension in ['.svg', '.png']:
            with open(filename + extension, 'rb') as f:
                files.append(f)
    
        return files





