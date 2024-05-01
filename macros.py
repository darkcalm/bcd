from discord import app_commands, File

from re import escape, sub

from wand.api import library
import wand.color
import wand.image

from agents import TextAgent, DrawingAgent

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
        return [sub(r'\\(.)', r'\1', s) for s in seed.split(';')]

    def flatten_seed(self, seed):
        return ';'.join(escape(x) for x in seed)

    def agents_check_requests(self, agents, requests):
        #inspect, facilitate, infers
        pass
    
    def text_to_seed(self, interaction, body):
        ta_ = [TextAgent(self.deflatten_seed(h.content), body['diagram']) for h in body['history']]

        for i, ta in enumerate(ta_):
            self.agents_check_requests(ta.agents, body['diagram'].requests)

            for a in ta.agents:
                a.observe()
            
            while any(ta.conflicts.values()):
                ta.facilitate()
                
            if i:
                ta.infer(ta_[i-1])

        return ta_[-1].seed

    async def seed_to_files(self, interaction, body, seed):
        da_ = [DrawingAgent(d, seed) for d in body['diagram']]
        
        for i, da in enumerate(da_):
            self.agents_check_requests(da.agents, body['diagram'].requests)

            for a in da.agents:
                a.observe()
            
            while any(da.conflicts.values()):
                da.facilitate()
                
            if i:
                da.infer(da_[i-1])
                
        fns = [da_[-1].diagram.name + '.svg', da_[-1].diagram.name + '.png']
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