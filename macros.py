from discord import app_commands, File

from random import shuffle
from itertools import product

from wand.api import library
import wand.color
import wand.image

from agents import TextAgent, DrawAgents

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

    def deflatten_seed(self, seed):
        #
        return seed

    def flatten_seed(self, seed):
        #
        return seed

    def reduce_seeds(self, textagents):
        seed = ""
        #
        return seed
    
    async def text_to_seed(self, interaction, body):
        h_ = body['history'].append([interaction])
        ta_ = [TextAgent(self.deflatten_seed(h.content), body['diagram']) for h in h_]

        for i, ta in enumerate(ta_):
            while any(ta.conflicts.values()):
                ta.inspects()
                ta.facilitates()
            if i:
                ta.infers(ta_[i-1])
        
        return ta_[-1].seed

    async def seed_to_files(self, interaction, diagram, seed):
        
        da = DrawAgents(diagram, seed)

        while any(da.conflicts.values()):
            da.inspects()
            da.facilitates(next(x for x in da.conflicts.values() if x))
            
        da.infers()
        
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
        
        await interaction.followup.send(self.flatten_seed(seed),
            files, ephemeral=not interaction.data.get('publish'))