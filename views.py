from discord import app_commands

class DiscordBotView:
    def __init__(self, delimiter):
        self.delimiter = delimiter
        self.choices = []

    def write_discord_choice(self, hash, diagram):
        self.choices.append(app_commands.Choice(name=diagram.name, value=hash))
    
    def get_diagram_info(self, diagram):
        return diagram.name + ":\n" + "\n".join([k+": "+v[0] for k, v in diagram.accepts.items()])

    def get_diagram_by_attachments(self, attachments):
        prompt = attachments[0].filename.lower().split('.', 1)[0]
        for c in self.choices:
            if prompt == c.name:
                return c.value