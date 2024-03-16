####	query processing START ####

import re

# regex ex. ^(1) ([^;]*)|; *(1) ([^;]*)[; ]* for queries ex. "1 foo;" or "; 1 foo"

DELIMITER = ';'
REGEX_VALUE_GROUPNUM = [1, 3]

def query_regex(key):
    return r"^(" + re.escape(key) + ") ([^" + DELIMITER + "]*)|" + DELIMITER + " *(" + re.escape(key) + ") ([^" + DELIMITER + "]*)[" + DELIMITER + " ]*" 

# a valid query is either 1) a complete assignment of diagram texts and settings, 2) a complete assignment of diagram texts, or 3) a partial assignment of diagram texts indicating what parts of the diagram to use

TEXT_SETTINGS_INDEX = 0
SETTINGS_UNSET_VALUE = None

def inputtoquery(input, diagram):
    _input = input
    input = input.strip(DELIMITER).split(DELIMITER)
    input = [q.strip(' ') for q in input]
    query = []
    
    if len(input) == len(diagram.get_all_option_keys()):
        for group in diagram.settings:
            query.append(dict(zip(group.keys(), input[:len(group)])))
            input = input[len(group):]
    
    elif len(input) == len(diagram.settings[TEXT_SETTINGS_INDEX].keys()):
        for group in diagram.settings:
            query.append(dict(zip(group.keys(), [SETTINGS_UNSET_VALUE]*len(group))))
        query[TEXT_SETTINGS_INDEX] = dict(zip(diagram.settings[TEXT_SETTINGS_INDEX].keys(), input))
    
    else:
        for group in diagram.settings:
            query.append({})
            for key in group.keys():
                find = re.findall(query_regex(key), _input)
                if (len(find) == 0):
                    query[-1][key] = SETTINGS_UNSET_VALUE
                else:
                    find = find[0]
                    query[-1][key] = find[REGEX_VALUE_GROUPNUM[0]] or find[REGEX_VALUE_GROUPNUM[1]]
            
    return query

def amendquery(oldquery, newquery):
    if not (oldquery and newquery):
        return oldquery or newquery
    for i, group in enumerate(newquery):
        for key, new_value in group.items():
            if new_value is SETTINGS_UNSET_VALUE:
                newquery[i][key] = oldquery[i][key]
    return newquery

def defaultdrive(query, diagram):
    for i, group in enumerate(diagram.defaults):
        for j, type in enumerate(group):
            values = list(query[i].values())
            if values[j] is SETTINGS_UNSET_VALUE:
                values[j] = diagram.defaults[i][j]
            elif isinstance(type, int):
                values[j] = int(float(values[j]))
            elif isinstance(type, str):
                values[j] = str(values[j])
            query[i] = dict(zip(diagram.settings[i].keys(), values))
    return query

def querytoseed(query, diagram):
    seed = ""
    for group in query:
        seed += DELIMITER.join([str(_) for _ in group.values()]) + DELIMITER
    seed = seed[:-len(DELIMITER)]
    return seed


####    query processing END ####



####    graphics START ####

from wand.api import library
import wand.color
import wand.image

from pyx import *

import svgutils.transform
import sys

def line_PyX(c, *args):
    c.stroke(path.line(*args), [style.linewidth.Thin])

# text requires pkgs.texlive.combined.scheme-basic (nix)
def text_PyX(c, text_content, *xy):
    c.text(*xy, text_content)

def filename_svg(name):
    return name +'.svg'

def filename_png(name):
    return name +'.png'

async def querytofile_PyX(query, diagram):
    c = canvas.canvas()

    for i, text in enumerate(list(query[TEXT_SETTINGS_INDEX].values())):
        diagram.agents[i]['mask'] = text
    
    for agent in diagram.agents:
        for do in agent['do']:
            if do == 'stationary':
                if agent['as'] == 'line':
                    line_PyX(c, *agent['at'][0], *agent['at'][1])
            else:
                if agent['as'] == 'text':
                    text_PyX(c, agent['mask'], *agent['at'])
                
    c.writeSVGfile(diagram.name)
    
    with wand.image.Image(resolution = 300) as image:
        with wand.color.Color('transparent') as background_color:
            library.MagickSetBackgroundColor(image.wand, 
                                             background_color.resource) 
        image.read(blob=open(filename_svg(diagram.name), "r").read().encode('utf-8'), format="svg")
        png_image = image.make_blob("png32")
    with open(filename_png(diagram.name), "wb") as out:
        out.write(png_image)

async def filetoscaled_svgutils(file, scalevalue):
    if file and file[0].filename.lower().endswith('.svg'):
        # scale svg with scalevalue
        pass

    
    pass


'''
# wrapping of text within a width
def getwrappedtext_PIL(text, wrapspan, font):
    def getspan(target, font):
        return font.getbbox(target)[2]

    def getdist(target, font):
        return font.getbbox(target)[3]

    textwrap = []
    span = 0
    lasti = 0
    for i in range(len(text)):
        # supports manual line breaks \n
        if text[i:i + 2] == '\\n':
            textwrap.append(text[lasti:i].strip("\n"))
            lasti = i + 2
            span = 0

        elif span + getspan(text[i], font) < wrapspan:
            span += getspan(text[i], font)

        else:
            # wrap through a single-word line
            span = 0
            if len(text[lasti:i].strip(" ").split(" ")) < 2:
                textwrap.append(text[lasti:i].strip(" "))
                lasti = i
            # wrap through a multi-word line
            else:
                append = " ".join(text[lasti:i].strip(" ").split(" ")[:-1])
                textwrap.append(append)
                lasti = lasti + len(append) + 1

    textwrap.append(text[lasti:].strip(" "))
    return "\n".join(textwrap)
'''

####	graphics END ####



####    diagram setup START ####

import math

class DiagramCommand:
    def __init__(self, name, settings, drive, agents):
        self.name = name
        self.settings = settings
        self.defaults = drive
        self.agents = agents

    def get_defaults(self):
        return self.defaults

    def get_agents(self):
        return self.agents
    
    def get_all_option_keys(self):
        settings = []
        for group in self.settings:
            for key in group:
                settings.append(key)
        return settings

    def get_info(self):
        info = []
        for group in self.settings:
            info.append("\n".join(
                [key + ": " + value for (key, value) in group.items()]))
        return "🤖️ command info: " + self.name + " 🤖️\n\n" + "\n".join(info) + "\n\n* use a ' ' after any label to start an assignment\n* use a ';' to separate assignments\n* given read permission on servers, it is possible to reply to bot responses in order to modify or add assignments, \n* if under the same format, it is possible to use the text in bot responses as a seed string to publish at the original channel\n* it is recommended that you try things in dms to see if the bot's working according to your needs :)"

# Create instances for twobytwo and twoofthree commands
diagrams = [
    DiagramCommand(
        "twobytwo",
        [{
            "t": "title",
            "1": "top right",
            "2": "top left",
            "3": "bottom left",
            "4": "bottom right",
            "xp": "when x is + (right)",
            "xn": "when x is - (left)",
            "yp": "when y is + (up)",
            "yn": "when y is - (down)",
            "x": "x axis label",
            "y": "y axis label"
        }, {
            "fs": "font size"
        }],
        [[''] * 11, ['scale=1']],
        [
            {'as': 'text', 'at': (0, 4), 'do': ['']},
            {'as': 'text', 'at': (3, 3), 'do': ['']},
            {'as': 'text', 'at': (1, 3), 'do': ['']},
            {'as': 'text', 'at': (1, 1), 'do': ['']},
            {'as': 'text', 'at': (3, 1), 'do': ['']},
            {'as': 'text', 'at': (4, 2), 'do': ['']},
            {'as': 'text', 'at': (0, 2), 'do': ['']},
            {'as': 'text', 'at': (2, 4), 'do': ['']},
            {'as': 'text', 'at': (2, 0), 'do': ['']},
            {'as': 'text', 'at': (3, 2), 'do': ['']},
            {'as': 'text', 'at': (2, 3), 'do': ['']},
            {'as': 'line', 'at': [(0, 2), (4, 2)], 'do': ['stationary']},
            {'as': 'line', 'at': [(2, 4), (2, 0)], 'do': ['stationary']}
        ]
    ), DiagramCommand(
        "twoofthree",
        [{
            "t": "title",
            "u": "up",
            "l": "left",
            "r": "right",
            "-u": "left-right pair",
            "-l": "right-up pair",
            "-r": "up-left pair"
        }, {
            "fs": "font size"
        }],
        [[''] * 7, ['scale=1']],
        [
            {'as': 'text', 'at': (2, 225), 'do': ['']},
            {'as': 'text', 'at': (1, 270), 'do': ['']},
            {'as': 'text', 'at': (1, 150), 'do': ['']},
            {'as': 'text', 'at': (1, 30), 'do': ['']},
            {'as': 'text', 'at': (0.618, 90), 'do': ['']},
            {'as': 'text', 'at': (0.618, 330), 'do': ['']},
            {'as': 'text', 'at': (0.618, 210), 'do': ['']},
            {'as': 'line', 'at': [(1, 150), (1, 30)], 'do': ['stationary']},
            {'as': 'line', 'at': [(1, 30), (1, 270)], 'do': ['stationary']},
            {'as': 'line', 'at': [(1, 270), (1, 150)], 'do': ['stationary']}
        ]
    )
]

def diagram_setup_processing(index):

    def helper_0(rtheta):
        (r, theta) = rtheta
        return (r * math.cos(theta/180*math.pi), -r * math.sin(theta/180*math.pi))

    def helper_1(xy, xy0):
        return (max([abs(xy[0]), abs(xy0[0])]), max([abs(xy[1]), abs(xy0[1])]))

    def f_add(l1, l2):
        return [l1[i] + l2[i] for i in range(len(l1))]
    
    if index == 1:

        persist = (0, 0)
    
        for agents in diagrams[index].agents:
            if agents['as'] == 'text':
                agents['at'] = helper_0(agents['at'])
                persist = helper_1(agents['at'], persist)
            elif agents['as'] == 'line':
                agents['at'][0] = helper_0(agents['at'][0])
                agents['at'][1] = helper_0(agents['at'][1])
                persist = helper_1(agents['at'][0], persist)
                persist = helper_1(agents['at'][1], persist)
    
        for agents in diagrams[index].agents:
            if agents['as'] == 'text':
                agents['at'] = f_add(agents['at'], persist)
            elif agents['as'] == 'line':
                agents['at'][0] = f_add(agents['at'][0], persist)
                agents['at'][1] = f_add(agents['at'][1], persist)

for i in range(len(diagrams)):
    diagram_setup_processing(i)

####    diagram setup END ####



####	 discord START ####

import os, traceback

import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

DIAGRAM_DICT = {}
DESCRIPTIONS = {}
for d in diagrams:
    DIAGRAM_DICT[d.name] = d
    DESCRIPTIONS[d.name] = "settings: " + ", ".join(d.get_all_option_keys())

DESCRIPTIONS['info'] = "syntax: option1 value1; option2 value2. enter specific diagram name for other information (sent to dm)."
DESCRIPTIONS['pub'] = "sets the output of the bot (default: private)"

MESSAGES = {
    'dm': "check dm :)",
    'dev': "🤖️ bug or typo? check command info or contact dev with:\n\n"
}

PUBLISH_DICT = {
    0: ['.svg', '.png'], 1: ['.svg'], 2: ['.png'], 3: ['.svg', '.png']
}

async def exceptionhandler(interaction, message=None):
    if message:
        await interaction.author.send(message)
    elif hasattr(interaction, 'author'):
        await interaction.author.send(MESSAGES['dev'] + str(traceback.format_exc()))
    else:
        await interaction.user.send(MESSAGES['dev'] + str(traceback.format_exc()))

async def commandhelper(interaction, pub, input, diagram):
    try:
        query = inputtoquery(input, diagram)
        query = defaultdrive(query, diagram)
        await querytofile_PyX(query, diagram)
        seed = querytoseed(query, diagram)
        files = []
        for extension in PUBLISH_DICT[pub]:
            with open(diagram.name + extension, 'rb') as f:
                files.append(discord.File(f))
        if hasattr(interaction, 'response'):
            await interaction.response.send_message(
                seed, files=files, ephemeral=False if pub>0 else True)
        else:
            await interaction.channel.send(seed, files=files)

    except Exception:
        await exceptionhandler(interaction)
            
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name='bcd')
@app_commands.describe(**DESCRIPTIONS)
@app_commands.choices(pub = [
    discord.app_commands.Choice(name='private', value=0),
    discord.app_commands.Choice(name='public/svg', value=1),
    discord.app_commands.Choice(name='public/png', value=2),
    discord.app_commands.Choice(name='public/both', value=3)
])
async def bcd(interaction: discord.Interaction,
              info: str = "",
              pub: int = 0,
              twobytwo: str = "",
              twoofthree: str = ""):

    for d in diagrams:
        if info == d.name:
            await interaction.user.send(d.get_info())
            await interaction.response.send_message(MESSAGES['dm'], ephemeral=True)
    
    if twobytwo != "":
        await commandhelper(interaction, pub, twobytwo, diagrams[0])

    if twoofthree != "":
        await commandhelper(interaction, pub, twoofthree, diagrams[1])

REPLY_DELETE = ['delete', 'd']
REPLY_SCALE = ['scale', 's']
REPLY_PASS = ['pass', '#']
REPLY_INFO = ['info', 'i']
@bot.event
async def on_message(interaction):
    if interaction.author.id == bot.user.id:
        return

    if interaction.reference and interaction.channel:
        message = await interaction.channel.fetch_message(
            interaction.reference.message_id)
        if hasattr(message, 'author'):
            if message.author.id == bot.user.id:
                if interaction.content in REPLY_DELETE:
                    await message.delete()
                elif interaction.content in REPLY_PASS:
                    pass
                elif interaction.content in REPLY_SCALE:
                    # get scalevalue
                    scalevalue = 1
                    await filetoscaled_svgutils(message.attachments, scalevalue)
                elif message.attachments:
                    reply_via = message.attachments[0].filename.lower().split('.')
                    if reply_via[0] in DIAGRAM_DICT.keys():
                        diagram = DIAGRAM_DICT[reply_via[0]]
                        if interaction.content in REPLY_INFO:
                            await interaction.channel.send(diagram.get_info())
                        else:
                            seed = querytoseed(amendquery(
                                inputtoquery(message.content, diagram),
                                inputtoquery(interaction.content, diagram)), diagram)
                            await commandhelper(interaction, 3, seed, diagram)

    
bot.run(TOKEN)

####    discord END ####


