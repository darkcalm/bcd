from presets import Protocols, Payload
from agents import SessionAgent

import discord
from discord.ext import commands

import os

sessions = {}

def append_session(token):
    sessions[token] = SessionAgent(token)
    return sessions[token]

choices = []

for name in Protocols.keys():
    choices.append(discord.app_commands.Choice(name=name, value=name))

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

@bot.tree.command(name='bcd', description = "generate diagrams. update diagrams through replies. use /bcd to see the list of diagrams.")
@discord.app_commands.describe(see_keys="(optional) provides a sample of an assign for the diagram in dm", diagram="choose which diagram to assign to", assign="recommend: key content; key content etc.", publish="send bcd outputs publicly")

@discord.app_commands.choices(
    see_keys = choices,
    diagram = choices,
    publish = [discord.app_commands.Choice(name='private', value=0), discord.app_commands.Choice(name='public', value=1)])

async def bcd(interaction: discord.Interaction,
              see_keys: str = "",
              diagram: str = "",
              assign: str = "",
              #request: str="",
              publish: int = 0):
    
    await interaction.response.defer()
    
    if diagram != "" or assign != "":
        sa = append_session(interaction.token)
        await sa.output(interaction, Payload(diagram+" <> ", assign), publish)
        del sa

    elif see_keys != "":
        await interaction.followup.send(see_keys + " <> " + "; ".join([
                k+" "+str(v) for k, v in Protocols[see_keys].keys.items()]))

    else:
        await interaction.user.send("🤔 unresponsive to input")


@bot.event
async def on_message(interaction):    
    if not bot.user:
        return
    if interaction.author.id == bot.user.id:
        return
    
    if interaction.reference is not None:                
        sa = append_session(interaction.reference.message_id)        
        reference = await interaction.channel.fetch_message(interaction.reference.message_id)
        
        if reference.author.id == bot.user.id:
            if interaction.content in ['delete', 'd']:
                await reference.delete()
            else:
                await sa.output(interaction, Payload(reference.content, interaction.content), True)

        del sa

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print("synced " + str(synced))
    except Exception as e:
        print(e)

token = os.environ['DISCORD_TOKEN']
bot.run(token)