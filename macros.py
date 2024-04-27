from discord import app_commands, File

from random import shuffle
from itertools import product

from wand.api import library
import wand.color
import wand.image

from agents import DiagramAgent, TextAgent, DrawAgents

class DiagramBotHelper:
    def __init__(self):
        self.choices = []

    def write_discord_choice(self, hash, diagram):
        self.choices.append(app_commands.Choice(name=diagram.name, value=hash))
    
    def get_diagram_info(self, diagram):
        return diagram.name + ":\n" + "\n".join([k+": "+v for k, v in diagram.options.items()])

    def get_diagram(self, message):
        prompt = message.attachments[0].filename.lower().split('.', 1)[0]
        for c in self.choices:
            if prompt == c.name:
                return c.value

    def validate_seed(self, diagram, seed):    # todo
        return True

    def update_seed(self, diagram, seed):      # todo  
        return seed
    
    async def text_to_seed(self, interaction, body):

        d = body['diagram']
        da_ = [DiagramAgent(k, v) for k, v in d.options.items()]
    
        t = body['history'].append([interaction])
        ta_ = [TextAgent(t) for t in t.content]
    
        seed = ""
        pa_ = list(product(da_, da_))
        while seed is not self.validate_seed(d, seed):
            shuffle(pa_)
            for ta in reversed(ta_):
                for pa in pa_:
                    ta.facilitates(pa)
            seed = self.update_seed(d, seed)

        return seed

    async def seed_to_files(self, interaction, diagram, seed):
        
        da = DrawAgents(diagram, seed)

        for a in da.agents:
            # run agents to inspect things
            pass

        while any(da.conflicts.values()):
            # agent does goals
            break
            
        da.inference()
        
        fns = [da.diagram.name + '.svg', da.diagram.name + '.png']
        with wand.image.Image(resolution = 300) as image:
            with wand.color.Color('white') as background_color:
                library.MagickSetBackgroundColor(image.wand, 
                                                 background_color.resource) 
            image.read(blob=open(fns[0], "r").read().encode('utf-8'), format="svg")
            png_blob = image.make_blob("png32")
        with open(fns[1], "wb") as out:
            out.write(png_blob)
        
        files = []
        for fn in fns:
            with open(fn, 'rb') as f:
                files.append(File(f))
        
        await interaction.followup.send(
            seed, files, ephemeral=not interaction.data.get('publish'))