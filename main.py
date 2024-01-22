####	infrastructure (infras) START ####

import re

SEED_DELIM_SUPRA = '//'
SEED_DELIM_INFRA = ';'

# regex ex. ^(1) ([^;]*)|; *(1) ([^;]*)[; ]* for seed strings ex. 1 good; or 1 bad
def INFRA_REGEX(param_name):
    return r"^(" + re.escape(
        param_name
    ) + ") ([^" + SEED_DELIM_INFRA + "]*)|" + SEED_DELIM_INFRA + " *(" + re.escape(
        param_name
    ) + ") ([^" + SEED_DELIM_INFRA + "]*)[" + SEED_DELIM_INFRA + " ]*" 


INFRA_VALUE_GROUPNUM = [1, 3]
INFRA_KEY_GROUPNUM = [0, 2]

def seedtoinfras(_seed, _OPTIONS):
    if _seed is None:
        return None

    strict_infras = _seed.split(SEED_DELIM_SUPRA)
    if len(strict_infras) == len(_OPTIONS):
        for i, optionsect in enumerate(_OPTIONS):
            strict_infras[i] = strict_infras[i].split(SEED_DELIM_INFRA)
            if len(strict_infras[i]) != len(optionsect):
                strict_infras = None
                break

    else:
        strict_infras = None
        
    if strict_infras:
        return strict_infras

    # parse and categorize input to parameters and image preferences
    _seed = _seed.replace(SEED_DELIM_SUPRA, SEED_DELIM_INFRA)
    match_bitmap = []
    infras = []

    for i, section_params in enumerate(_OPTIONS):
        match_result = []
        infras.append([])

        for key in section_params:
            match_result.append(re.findall(INFRA_REGEX(key), _seed))
            infras[i].append([])
        # separated for alias keys if any
        for j, key in enumerate(section_params):
            if match_result[j] != []:
                infras[i][j] = match_result[j][-1][INFRA_VALUE_GROUPNUM[
                    0]] or match_result[j][-1][INFRA_VALUE_GROUPNUM[1]]
            else:
                infras[i][j] = None
    
        match_bitmap.append(match_result != [[]] * len(section_params))

    if match_bitmap == [False] * len(_OPTIONS):
        return False

    return infras

def amendinfras(oldinfras, newinfras):
    if not (oldinfras and newinfras):
        return oldinfras or newinfras
    for i, section in enumerate(newinfras):
        for j, new_value in enumerate(section):
            if new_value == None:
                newinfras[i][j] = oldinfras[i][j]
        
    return newinfras

def infrastoseed(infras):
    _seed = ""
    for i, section in enumerate(infras):
        for j, value in enumerate(section):
            _seed += str(value) + SEED_DELIM_INFRA   
        _seed = _seed[:-len(SEED_DELIM_INFRA)]
        _seed += SEED_DELIM_SUPRA
    _seed = _seed[:-len(SEED_DELIM_SUPRA)]
    return _seed

def typedrive(infras, infras0):
    for i, section in enumerate(infras0):
        for j, value in enumerate(section):
            if isinstance(value, int):
                infras[i][j] = int(float(infras[i][j]))
            elif isinstance(value, str):
                infras[i][j] = str(infras[i][j])
    return infras


####    infrastructure (infras) END ####

####	 discord START ####

import os, traceback

import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.environ['DISCORD_BOT_TOKEN']

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


# A handler is used for ongoing events
MESSAGE_D = "🤖️ bug or typo? check command info or contact dev with:\n\n"


async def exceptionhandler(interaction, message=None):
    if message:
        await interaction.author.send(message)
    elif hasattr(interaction, 'author'):
        await interaction.author.send(MESSAGE_D + str(traceback.format_exc()))
    else:
        await interaction.user.send(MESSAGE_D + str(traceback.format_exc()))


# This event is triggered for every message that the bot can see
COMMANDS = ["twobytwo", "twoofthree"]
REPLY_DELETE = ['delete', 'd']
REPLY_COMMENT = ['comment', '#']
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

                elif interaction.content in REPLY_COMMENT:
                    pass

                elif interaction.content in REPLY_INFO:
                    c = message.attachments[0].filename.lower()[:-4]
                    if c in COMMANDS:
                        await interaction.channel.send(getinfo(c))

                elif message.attachments:
                    c = message.attachments[0].filename.lower()[:-4]
                    if c in COMMANDS:
                        infras0 = seedtoinfras(message.content,
                                              eval(c + "_OPTIONS"))
                        infras0 = typedrive(infras0, eval(c + "_INFRAS0"))
                        await commandhelper(
                            interaction, True, interaction.content, infras0, c)


async def commandhelper(interaction, _pub, _seed, name):
    try:
        infras = seedtoinfras(_seed, eval(name + "_OPTIONS"))
        infras = amendinfras(eval(name + "_INFRAS0"), infras)  #fallback
        infras = typedrive(infras, eval(name + "_INFRAS0"))
        infrastofile_PIL(infras, name, eval(name + "_EXE"))
        _seed = infrastoseed(infras)
        with open(name + ".png", 'rb') as f:
            if hasattr(interaction, 'response'):
                await interaction.response.send_message(
                    _seed if _pub == True else _seed,
                    file=discord.File(f),
                    ephemeral=not _pub)
            else:
                await interaction.channel.send(_seed, file=discord.File(f))

    except Exception:
        await exceptionhandler(interaction)

####    discord END ####



    
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


def infrastofile_PIL(infras, name, _EXE):
    # notations
    (_tilewidth, _tileheight, _fontsize) = infras[-1]
    _texts = infras[-2]
    
    # interfaces
    def text(xy_principle, posture):
        text_PIL(f_add(xy_principle, posture[2]),
                 posture[0], posture[1], PILfont, PILimage)

    def line(xy_principle, posture1, xy2, posture2): # principle ~ larger
        line_PIL(f_add(xy2, posture2) + f_add(xy_principle, posture1), PILdraw)

    def gettextsize(indexortext):
        if isinstance(indexortext, int):
            return getsize_PIL(gettextposture(indexortext)[1], PILfont, PILimage)
        if isinstance(indexortext, str):
            return getsize_PIL(indexortext, PILfont, PILimage)

    # macros
    def f_coordinates(xy, mode="cartesian"):
        if mode == "cartesian":
            return f_mul(xy, (_tilewidth, _tileheight))

    def gettextposture(i, postureparam=None):
        if postureparam is None:
            postureparam = _EXE[i]['posture']
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
    _EXE_runtime = []
    for i, _ in enumerate(_EXE):
        if _['mode'] == 'text':
            _EXE_runtime.append(
                {'mode': 'text',
                 'xy_principle': f_coordinates(_['position']),
                 'posture': gettextposture(i, _['posture'])})
        elif _['mode'] == 'line':
            _EXE_runtime.append(
                {'mode': 'line',
                 'xy2': f_coordinates(_['position'][0]),
                 'posture2': getlineposture(_['posture'][0]),
                 'xy_principle': f_coordinates(_['position'][1]),
                 'posture1': getlineposture(_['posture'][1])})

        PILimage, PILdraw, PILfont = getresources_PIL(
            f_int(f_max(_EXE_runtime[-1]['xy_principle'], srcimage.size)), _fontsize)
        PILimage.paste(srcimage, (0, 0) + srcimage.size)
        srcimage = PILimage

    # execution
    for i, _ in enumerate(_EXE_runtime):
        if _['mode'] == 'text':
            del _EXE_runtime[i]['mode']
            text(**_EXE_runtime[i])
        elif _['mode'] == 'line':
            del _EXE_runtime[i]['mode']
            line(**_EXE_runtime[i])

    PILimage.save(name + '.png')


####	PIL END ####





####    bcd commons START ####

COMMAND_DESCRIPTION_COMMON = {
    'info': "type command name to see what's available for that command (sent to dm)",
    'twobytwo': "syntax: 1 foo" + SEED_DELIM_INFRA + " 2 bar" + SEED_DELIM_INFRA +
        " fs 42 ...",
    'twoofthree': "under construction 🤖️",
    'publish': "sets if channel sees the bot's reply (default is False)"
}

COMMAND_INFO_COMMON_POST = "\n\n* use a ' ' after any label to start an assignment\n* use a ';' to separate assignments\n* it is possible to reply to bot responses in order to modify or add assignments\n* it is possible to use the text in bot responses as a seed string to publish at the original channel\n* it its recommended that you try things here with the bot, so you can see what's going on, or if it's working according to your needs :)"

def COMMAND_INFO_COMMON_PRE(name):
    return "🤖️ command info: " + name + " 🤖️\n\n"

def getoptions(DESCRIPTIONS):
    options = []
    for section in DESCRIPTIONS:
        options.append([key.lstrip('_') for key in section.keys()])
    return options

def getinfo(name):
    info = []
    for section in eval(name + "_DESCRIPTIONS"):
        info.append("\n".join(
            [key + ": " + value for (key, value) in section.items()]))
    return COMMAND_INFO_COMMON_PRE(name) + "\n".join(info) + COMMAND_INFO_COMMON_POST

@bot.tree.command(name='bcd')
@app_commands.describe(**COMMAND_DESCRIPTION_COMMON)
async def bcd(interaction: discord.Interaction,
              info: str = None,
              twobytwo: str = None,
              twoofthree: str = None,
              publish: bool = False):

    if info is not None:        
        await interaction.user.send(getinfo(info))
        await interaction.response.send_message("check dm :)", ephemeral=True)
    
    elif twobytwo is not None:
        await commandhelper(interaction, publish, twobytwo, twobytwo_NAME)

    elif twoofthree is not None:
        await commandhelper(interaction, publish, twoofthree, twoofthree_NAME)


####    bcd commons END ####

import math

####    twobytwo START ####

twobytwo_NAME = "twobytwo"

twobytwo_DESCRIPTIONS = [{
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
    "tw": "tile width",
    "th": "tile height",
    "fs": "font size"
}]

twobytwo_OPTIONS = getoptions(twobytwo_DESCRIPTIONS)

twobytwo_INFRAS0 = [[''] * 11, [200, 200, 24]]

twobytwo_EXE = [
    {'mode': 'text', 'position': (0, 0), 'posture': [2, 'la', (0, 0)]},
    {'mode': 'text', 'position': (3, 1), 'posture': [2, 'mm', (0, 0)]},
    {'mode': 'text', 'position': (1, 1), 'posture': [2, 'mm', (0, 0)]},
    {'mode': 'text', 'position': (1, 3), 'posture': [2, 'mm', (0, 0)]},
    {'mode': 'text', 'position': (3, 3), 'posture': [2, 'mm', (0, 0)]},
    {'mode': 'text', 'position': (4, 2), 'posture': [2, 'rm', (0, 0)]},
    {'mode': 'text', 'position': (0, 2), 'posture': [2, 'lm', (0, 0)]},
    {'mode': 'text', 'position': (2, 0), 'posture': [2, 'ma', (0, 0)]},
    {'mode': 'text', 'position': (2, 4), 'posture': [2, 'md', (0, 0)]},
    {'mode': 'text', 'position': (3, 2), 'posture': [1, 'ra', (0, 0)]},
    {'mode': 'text', 'position': (2, 1), 'posture': [.5, 'ra', (0, 0)]},
    {'mode': 'line', 'position': [(0, 2), (4, 2)], 'posture': [(6, [1, 0]), (5, [-1, 0])]},
    {'mode': 'line', 'position': [(2, 0), (2, 4)], 'posture': [(7, [0, 1]), (8, [0, -1])]}
]

####    twobytwo END ####

####    twoofthree START ####

twoofthree_NAME = "twoofthree"

twoofthree_DESCRIPTIONS = [{
    "t": "title",
    "u": "up",
    "l": "left",
    "r": "right",
    "-u": "left-right pair",
    "-l": "right-up pair",
    "-r": "up-left pair"
}, {
    "tw": "tile width",
    "th": "tile height",
    "fs": "font size"
}]

twoofthree_OPTIONS = getoptions(twoofthree_DESCRIPTIONS)

twoofthree_INFRAS0 = [[''] * 7, [200, 200, 24]]

twoofthree_EXE = [
    {'mode': 'text', 'position': (2.4, 315), 'posture': [2, 'rs', (0, 0)]},
    {'mode': 'text', 'position': (1, 90), 'posture': [2, 'mt', (0, -1)]},
    {'mode': 'text', 'position': (1, 210), 'posture': [1, 'rt', (0, 0)]},
    {'mode': 'text', 'position': (1, 330), 'posture': [1, 'lt', (0, 0)]},
    {'mode': 'text', 'position': (0.618, 270), 'posture': [1, 'mt', (0, 0)]},
    {'mode': 'text', 'position': (0.618, 150), 'posture': [1, 'rs', (0, 0)]},
    {'mode': 'text', 'position': (0.618, 30), 'posture': [1, 'ls', (0, 0)]},
    {'mode': 'line', 'position': [(1, 210), (1, 330)], 'posture': [(0, [0, 0]), (0, [0, 0])]},
    {'mode': 'line', 'position': [(1, 330), (1, 90)], 'posture': [(0, [0, 0]), (0, [0, 0])]},
    {'mode': 'line', 'position': [(1, 90), (1, 210)], 'posture': [(0, [0, 0]), (0, [0, 0])]}
]

def twoofthree_pre():
    
    def twoofthree_helper_0(rtheta):
        (r, theta) = rtheta
        return (r * math.cos(theta/180*math.pi), -r * math.sin(theta/180*math.pi))
    
    def twoofthree_helper_1(xy, xy0):
        return (max([abs(xy[0]), abs(xy0[0])]), max([abs(xy[1]), abs(xy0[1])]))

    def f_add(l1, l2):
        return [l1[i] + l2[i] for i in range(len(l1))]
    
    twoofthree_persist = (0, 0)
    
    for exe in twoofthree_EXE:
        if exe['mode'] == 'text':
            exe['position'] = twoofthree_helper_0(exe['position'])
            twoofthree_persist = twoofthree_helper_1(exe['position'], twoofthree_persist)
        elif exe['mode'] == 'line':
            exe['position'][0] = twoofthree_helper_0(exe['position'][0])
            exe['position'][1] = twoofthree_helper_0(exe['position'][1])
            twoofthree_persist = twoofthree_helper_1(exe['position'][0], twoofthree_persist)
            twoofthree_persist = twoofthree_helper_1(exe['position'][1], twoofthree_persist)
    
    for exe in twoofthree_EXE:
        if exe['mode'] == 'text':
            exe['position'] = f_add(exe['position'], twoofthree_persist)
        elif exe['mode'] == 'line':
            exe['position'][0] = f_add(exe['position'][0], twoofthree_persist)
            exe['position'][1] = f_add(exe['position'][1], twoofthree_persist)
    
    pass

twoofthree_pre()

####    twoofthree END ####





bot.run(TOKEN)
