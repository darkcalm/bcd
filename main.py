import agents

from bots import DiscordBotView
from history import places

import discord
from discord.ext import commands
import asyncio

from actions import Epoch
import os

view = DiscordBotView(delimiter=';')

for hash, diagram in places.items():
    view.write_discord_choice(hash, diagram)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

@bot.tree.command(name='bcd', description = "generate diagram with /bcd. update by replying to bcd outputs")
@discord.app_commands.describe(diagram="choose diagram to assign to", assignments="syntax: t my_title" + view.delimiter + " label my_label" + view.delimiter + " etc.", publish="send message publicly", about="read what each label means for a diagram (to dm)")

@discord.app_commands.choices(
    diagram = view.choices,
    publish = [discord.app_commands.Choice(name='private', value=0), discord.app_commands.Choice(name='public', value=1)],
    about = view.choices)

async def bcd(interaction: discord.Interaction,
              diagram: str = "",
              assignments: str = "",
              publish: int = 0,
              about: str = ""):

    if diagram != "":
        await interaction.response.defer()
        await asyncio.sleep(5)
        await bcdoutput(interaction, publish, assignments, places[diagram])

    elif about != "":
        await interaction.user.send(view.get_diagram_info(places[diagram]))
    
    else:
        await interaction.user.send("🤔 unresponsive to input")

@bot.event
async def on_message(interaction):
    if interaction.author.id == bot.user.id:
        return
    
    message = await interaction.channel.fetch_message(interaction.reference.message_id)
    if message.author.id == bot.user.id:
        if interaction.content in ['comment', '#']:
            pass
        elif interaction.content in ['delete', 'd']:
            await message.delete()
        elif message.attachments:
            await bcdoutput(interaction, True,
                            [message.content, interaction.content],
                            view.get_diagram_by_attachments(message.attachments))


async def bcdoutput(interaction, publish, texts, diagram):
    epoch = Epoch(delimiter=';')
    seeds = await epoch.texts_to_seeds(texts, diagram)
    files = await epoch.seeds_to_files(seeds, diagram.name)
    await interaction.followup.send(
        seeds, files=[discord.File(f) for f in files], ephemeral=not publish)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print("synced " + str(synced))
    except Exception as e:
        print(e)

token = os.environ['DISCORD_TOKEN']
bot.run(token)