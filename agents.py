import asyncio
import os.path

from pyx import canvas, path
# for pyx text, import using nix: pkgs.texlive.combined.scheme-basic

from discord import File

from wand.color import Color
from wand.image import Image

class SessionAgent:
    def __init__(self, token):
        self.token = token

    async def output(self, interaction, payload, publish):
        await interaction.response.defer()
        await asyncio.sleep(5)
        
        path = os.path.join(self.token)

        SimulationAgent([KeyAgent(self) for h in payload.diagram.keys.keys()]).converge() #check converge

        SimulationAgent([RequestAgent(self) for r in payload.diagram.requests]).converge()

        self.draw_PyX(payload['requests'])
        
        with Color('white') as b:
            with Image(filename=path+'.svg', format='svg', background=b) as i:
                png_image = i.make_blob('png32')
                with open(path+'.png', 'wb') as out:
                    out.write(png_image)

        files = []
        for p in [path+'.svg', path+'.png']:
            with open(p, 'rb') as f:
                files.append(File(f))

        await interaction.followup.send(diagram.printedseed(payload),
            files, ephemeral=not interaction.data.get('publish'))
    
    def draw_PyX(self, requests):
        c = canvas.canvas()    
        for r in requests:
            if r.type == 'line':
                c.stroke(path.line(*r.args))
            elif r.type == 'text':
                c.text(*r.args)

        c.writeSVGfile(path) 
        
        
class SimulationAgent:
    def __init__(self):
        self.time = 0

    async def run(self, agents):
        pass
        

class KeyAgent:
    def __init__(self, parent):
        self.parent = parent


    def orient(self):
        pass


class RequestAgent:
    def __init__(self, parent):
        self.parent = parent

        pass

    #some kind of tool use