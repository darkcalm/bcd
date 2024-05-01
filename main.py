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
@discord.app_commands.describe(diagram="choose which diagram to assign to", information="(optional) provides a sample of an assignment for the diagram in dm", assignment="recommend: key content; key content etc.", publish="send bcd outputs publicly")

@discord.app_commands.choices(
    diagram = choices,
    information = choices,
    publish = [discord.app_commands.Choice(name='private', value=0), discord.app_commands.Choice(name='public', value=1)])

async def bcd(interaction: discord.Interaction,
              diagram: str = "",
              information: str = "",
              assignment: str = "",
              publish: int = 0):
    
    if diagram != "":
        sa = append_session(interaction.token)
        await sa.output(interaction, Payload(assignment, diagram), publish)
        del sa

    elif information != "":
        await interaction.user.send(information + "% " + "; ".join([
                k+" "+v for k, v in Protocols[information].keys.items()]))

    else:
        await interaction.user.send("🤔 unresponsive to input")


@bot.event
async def on_message(interaction):    
    if not bot.user:
        return
    if interaction.author.id == bot.user.id:
        return

    sa = append_session(interaction.token)
    
    if interaction.reference is not None:                
        reference = await interaction.channel.fetch_message(interaction.reference.message_id)
        if reference.author.id == bot.user.id:
            if interaction.content in ['delete', 'd']:
                await reference.delete()

            else:
                await sa.output(interaction,
                                Payload(interaction.content,
                                        previous=reference.content), True)

    else:
        await sa.output(interaction, Payload(interaction.content), True)

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