####	query processing START ####

import re

delimiter = ';'

# regex ex. ^(1) ([^;]*)|; *(1) ([^;]*)[; ]* for seed strings ex. 1 good; or 1 bad
def seed_regex(key):
    return r"^(" + re.escape(key) + ") ([^" + delimiter + "]*)|" + delimiter + " *(" + re.escape(key) + ") ([^" + delimiter + "]*)[" + delimiter + " ]*" 

value_groups = [1, 3]
basic_option_index = 0

def inputtoquery(input, diagram):
    _input = input
    input = input.strip(delimiter).split(delimiter)
    input = [q.strip(' ') for q in input]
    query = []
    
    if len(input) == len(diagram.get_all_option_keys()):
        for group in diagram.options:
            query.append(dict(zip(group.keys(), input[:len(group)])))
            input = input[len(group):]
    
    elif len(input) == len(diagram.options[basic_option_index].keys()):
        for group in diagram.options:
            query.append(dict(zip(group.keys(), [None]*len(group))))
        query[basic_option_index] = dict(zip(diagram.options[basic_option_index].keys(), input))
    
    else:
        for group in diagram.options:
            query.append({})
            for key in group.keys():
                find = re.findall(seed_regex(key), _input)
                if (len(find) == 0):
                    query[-1][key] = None
                else:
                    find = find[0]
                    query[-1][key] = find[value_groups[0]] or find[value_groups[1]]
            
    return query

def amendquery(oldquery, newquery):
    if not (oldquery and newquery):
        return oldquery or newquery
    for i, group in enumerate(newquery):
        for key, new_value in group.items():
            if new_value is None:
                newquery[i][key] = oldquery[i][key]
    return newquery

def defaultdrive(query, diagram):
    for i, group in enumerate(diagram.defaults):
        for j, type in enumerate(group):
            values = list(query[i].values())
            if values[j] is None:
                values[j] = diagram.defaults[i][j]
            elif isinstance(type, int):
                values[j] = int(float(values[j]))
            elif isinstance(type, str):
                values[j] = str(values[j])
            query[i] = dict(zip(diagram.options[i].keys(), values))
    return query

def querytoseed(query, diagram):
    seed = ""
    for group in query:
        seed += delimiter.join([str(_) for _ in group.values()]) + delimiter
    seed = seed[:-len(delimiter)]
    return seed


####    query processing END ####



####    graphics START ####

from wand.api import library
import wand.color
import wand.image

from pyx import *

def line_PyX(c, *args):
    c.stroke(path.line(*args), [style.linewidth.Thin])

# text requires pkgs.texlive.combined.scheme-basic in nix
def text_PyX(c, text_content, *xy):
    c.text(*xy, text_content)

def querytofile_PyX(query, diagram):
    c = canvas.canvas()

    for i, text in enumerate(list(query[basic_option_index].values())):
        diagram.agents[i]['mask'] = text
    
    for agents in diagram.agents:
        if agents['do'] == 'stationary':
            if agents['as'] == 'line':
                line_PyX(c, *agents['at'][0], *agents['at'][1])

    for agents in diagram.agents:
        if agents['do'] != 'stationary':
            if agents['as'] == 'text':
                text_PyX(c, agents['mask'], *agents['at'])
    
    c.writeSVGfile(diagram.name)

    with wand.image.Image(resolution = 300) as image:
        with wand.color.Color('transparent') as background_color:
            library.MagickSetBackgroundColor(image.wand, 
                                             background_color.resource) 
        image.read(blob=open(diagram.name + '.svg', "r").read().encode('utf-8'), format="svg")
        png_image = image.make_blob("png32")
    with open(diagram.name + '.png', "wb") as out:
        out.write(png_image)




####	graphics END ####


"""
####	PIL START ####
# https://pillow.readthedocs.io/en/stable/handbook/
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

global BACKGROUND_COLOR, FONT_COLOR, LINE_WIDTH, FITS

BACKGROUND_COLOR = (255, 255, 255)
FONT_COLOR = (0, 0, 0)
LINE_WIDTH = 1


def getresources_PIL(imagesize, fontsize):
    font = ImageFont.truetype('OpenSansEmoji.ttf', fontsize)
    PILimage = Image.new('RGB', imagesize, color=BACKGROUND_COLOR)
    PILdraw = ImageDraw.Draw(PILimage)
    return PILimage, PILdraw, font


# descent: https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
def getsize_PIL(textwrap, font, PILimage):
    with Pilmoji(PILimage) as pilmoji:
        size = pilmoji.getsize(textwrap, font=font)    # hotfixed core.py, helpers.py
        return [size[0], size[1] + font.getmetrics()[1]]


# textwrapped is a string with potentially some line-breaks ("\n")
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


def line_PIL(xyxy, PILdraw):
    PILdraw.line([(xyxy[0], xyxy[1]), (xyxy[2], xyxy[3])], width=LINE_WIDTH, fill=FONT_COLOR)


def text_PIL(xy, anchor, wrappedtext, font, PILimage):
    with Pilmoji(PILimage) as pilmoji:
        pilmoji.text(xy,
                     anchor=anchor,
                     text=wrappedtext,
                     font=font,
                     fill=FONT_COLOR)


def querytofile_PIL(query, diagram):
    # notations
    (_tilewidth, _tileheight, _fontsize) = query[-1].values()
    _texts = list(query[basic_option_index].values())

    # interfaces
    def text(xy_principle, posture):
        text_PIL(f_add(xy_principle, posture[2]),
                 posture[0], posture[1], PILfont, PILimage)

    def line(xy_principle, posture1, xy2, posture2): # principle ~ larger
        line_PIL(f_add(xy2, posture2) + f_add(xy_principle, posture1), PILdraw)

    def gettextsize(indexortext):
        if isinstance(indexortext, int): # index of agentscuting elements
            return getsize_PIL(gettextposture(indexortext)[1], PILfont, PILimage)
        if isinstance(indexortext, str):
            return getsize_PIL(indexortext, PILfont, PILimage)

    # macros
    def f_coordinates(xy, mode="cartesian"):
        if mode == "cartesian":
            return f_mul(xy, (_tilewidth, _tileheight))

    def gettextposture(i, postureparam=None):
        if postureparam is None:
            postureparam = diagram.agents[i]['do']
        (spanmax, singlelineanchor, multilinevector) = postureparam
        wrappedtext = getwrappedtext_PIL(_texts[i], spanmax*_tilewidth, PILfont)
        multilinevector = f_mul(gettextsize(wrappedtext), multilinevector)
        return (singlelineanchor, wrappedtext, multilinevector)

    def getlineposture(postureparam):
        return f_mul(gettextsize(postureparam[0]), postureparam[1])

    # micros
    def f_max(l1, l2):
        return [max(a, b) for a, b in zip(l1, l2)]

    def f_add(l1, l2):
        return [l1[i] + l2[i] for i in range(len(l1))]

    def f_mul(l1, l2):
        return [l1[i] * l2[i] for i in range(len(l1))]

    def f_int(l):
        return [int(a) for a in l]

    # resource
    srcimage = Image.new('RGB', (0, 0))
    PILimage, PILdraw, PILfont = getresources_PIL(srcimage.size, _fontsize)
    agents_runtime = []
    for i, agents in enumerate(diagram.agents):
        if agents['as'] == 'text':
            agents_runtime.append(
                {'as': 'text',
                 'xy_principle': f_coordinates(agents['at']),
                 'posture': gettextposture(i, agents['do'])})
        elif agents['as'] == 'line':
            agents_runtime.append(
                {'as': 'line',
                 'xy2': f_coordinates(agents['at'][0]),
                 'posture2': getlineposture(agents['do'][0]),
                 'xy_principle': f_coordinates(agents['at'][1]),
                 'posture1': getlineposture(agents['do'][1])})

        # make as big what will be drawn
        PILimage, PILdraw, PILfont = getresources_PIL(
            f_int(f_max(agents_runtime[-1]['xy_principle'], srcimage.size)), _fontsize)
        PILimage.paste(srcimage, (0, 0) + srcimage.size)
        srcimage = PILimage

    # agentscution
    for i, agents in enumerate(agents_runtime):
        if agents['as'] == 'text':
            del agents_runtime[i]['as']
            text(**agents_runtime[i])
        elif agents['as'] == 'line':
            del agents_runtime[i]['as']
            line(**agents_runtime[i])

    PILimage.save(diagram.name + '.png')


####	PIL END ####
"""


####    diagram setup START ####

import math

class DiagramCommand:
    def __init__(self, name, options, drive, agents):
        self.name = name
        self.options = options
        self.defaults = drive
        self.agents = agents

    def get_defaults(self):
        return self.defaults

    def get_agents(self):
        return self.agents
    
    def get_all_option_keys(self):
        options = []
        for group in self.options:
            for key in group:
                options.append(key)
        return options

    def get_info(self):
        info = []
        for group in self.options:
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
        [[''] * 11, [None]],
        [
            {'as': 'text', 'at': (0, 4), 'do': [2, 'la', (0, 0)]},
            {'as': 'text', 'at': (3, 3), 'do': [2, 'mm', (0, 0)]},
            {'as': 'text', 'at': (1, 3), 'do': [2, 'mm', (0, 0)]},
            {'as': 'text', 'at': (1, 1), 'do': [2, 'mm', (0, 0)]},
            {'as': 'text', 'at': (3, 1), 'do': [2, 'mm', (0, 0)]},
            {'as': 'text', 'at': (4, 2), 'do': [2, 'rm', (0, 0)]},
            {'as': 'text', 'at': (0, 2), 'do': [2, 'lm', (0, 0)]},
            {'as': 'text', 'at': (2, 4), 'do': [2, 'ma', (0, 0)]},
            {'as': 'text', 'at': (2, 0), 'do': [2, 'md', (0, 0)]},
            {'as': 'text', 'at': (3, 2), 'do': [1, 'ra', (0, 0)]},
            {'as': 'text', 'at': (2, 3), 'do': [.5, 'ra', (0, 0)]},
            {'as': 'line', 'at': [(0, 2), (4, 2)], 'do': 'stationary'},
            {'as': 'line', 'at': [(2, 4), (2, 0)], 'do': 'stationary'}
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
        [[''] * 7, [None]],
        [
            {'as': 'text', 'at': (2, 225), 'do': [2, 'rs', (0, 0)]},
            {'as': 'text', 'at': (1, 270), 'do': [2, 'mt', (0, -1)]},
            {'as': 'text', 'at': (1, 150), 'do': [1, 'rt', (0, 0)]},
            {'as': 'text', 'at': (1, 30), 'do': [1, 'lt', (0, 0)]},
            {'as': 'text', 'at': (0.618, 90), 'do': [1, 'mt', (0, 0)]},
            {'as': 'text', 'at': (0.618, 330), 'do': [1, 'rs', (0, 0)]},
            {'as': 'text', 'at': (0.618, 210), 'do': [1, 'ls', (0, 0)]},
            {'as': 'line', 'at': [(1, 150), (1, 30)], 'do': 'stationary'},
            {'as': 'line', 'at': [(1, 30), (1, 270)], 'do': 'stationary'},
            {'as': 'line', 'at': [(1, 270), (1, 150)], 'do': 'stationary'}
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

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

DIAGRAM_DICT = {}
DESCRIPTIONS = {}
for d in diagrams:
    DIAGRAM_DICT[d.name] = d
    DESCRIPTIONS[d.name] = "options: " + ", ".join(d.get_all_option_keys())

DESCRIPTIONS['info'] = "syntax: option1 value1; option2 value2. enter specific diagram name for other information (sent to dm)."
DESCRIPTIONS['pub'] = "sets the output of the bot (default: private)"

MESSAGES = [
    "check dm :)",
    "🤖️ bug or typo? check command info or contact dev with:\n\n"
] 

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
            await interaction.response.send_message(MESSAGES[0], ephemeral=True)
    
    if twobytwo != "":
        await commandhelper(interaction, pub, twobytwo, diagrams[0])

    if twoofthree != "":
        await commandhelper(interaction, pub, twoofthree, diagrams[1])

async def exceptionhandler(interaction, message=None):
    if message:
        await interaction.author.send(message)
    elif hasattr(interaction, 'author'):
        await interaction.author.send(MESSAGES[1] + str(traceback.format_exc()))
    else:
        await interaction.user.send(MESSAGES[1] + str(traceback.format_exc()))


REPLY_DELETE = ['delete', 'd']
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


async def commandhelper(interaction, pub, input, diagram):
    try:
        query = inputtoquery(input, diagram)
        query = defaultdrive(query, diagram)
        querytofile_PyX(query, diagram)
        seed = querytoseed(query, diagram)
        files = []
        for extension in {
            0: ['.svg', '.png'], 1: ['.svg'], 2: ['.png'], 3: ['.svg', '.png']
        }[pub]:
            with open(diagram.name + extension, 'rb') as f:
                files.append(discord.File(f))
        if hasattr(interaction, 'response'):
            await interaction.response.send_message(
                seed, files=files, ephemeral=False if pub>0 else True)
        else:
            await interaction.channel.send(seed, files=files)

    except Exception:
        await exceptionhandler(interaction)


####    discord END ####


bot.run(TOKEN)
