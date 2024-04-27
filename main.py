from presets import Protocols
from macros import DiagramBotHelper

import discord
from discord.ext import commands

import os
import asyncio

dba = DiagramBotHelper()

for hash, diagram in Protocols.items():
    dba.write_discord_choice(hash, diagram)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

@bot.tree.command(name='bcd', description = "generate diagrams. update bcd diagrams through replies. use /bcd to see the list of diagrams.")
@discord.app_commands.describe(diagram="choose diagram to assign to", options="what the assignment options are for a diagram (dm)", assignment="recommend: t my_title; q1 my_q1; etc.", publish="send message publicly")

@discord.app_commands.choices(
    diagram = dba.choices,
    options = dba.choices,
    publish = [discord.app_commands.Choice(name='private', value=0), discord.app_commands.Choice(name='public', value=1)])

async def bcd(interaction: discord.Interaction,
              diagram: str = "",
              options: str = "",
              assignment: str = "",
              publish: int = 0):

    if diagram != "":
        await interaction.response.defer()
        await asyncio.sleep(5)
        await bcdoutput(interaction, {'diagram': Protocols[diagram],
                                      'history': []}, publish)

    elif options != "":
        await interaction.user.send(dba.get_diagram_info(Protocols[diagram]))
    
    else:
        await interaction.user.send("🤔 unresponsive to input")

@bot.event
async def on_message(interaction):
    if interaction.author.id == bot.user.id:
        return
    if interaction.reference is None:
        return
    if interaction.reference.message_id is None:
        return
    
    message = await interaction.channel.fetch_message(interaction.reference.message_id)
    if message.author.id != bot.user.id:
        return
        
    if interaction.content in ['comment', '#']:
        pass
    elif interaction.content in ['delete', 'd']:
        await message.delete()
        
    elif message.attachments:
        await bcdoutput(
            interaction,
            {'diagram': dba.get_diagram(message),
             'history': [message]}, True)

async def bcdoutput(interaction, body, publish):
    seed = await dba.text_to_seed(interaction, body)
    await dba.seed_to_files(interaction, body['diagram'], seed)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print("synced " + str(synced))
    except Exception as e:
        print(e)

token = os.environ['DISCORD_TOKEN']
bot.run(token)