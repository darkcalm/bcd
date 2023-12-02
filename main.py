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
MESSAGE_D = "🤖️ bug or typo? check out the command descriptions or contact dev with:\n\n"


async def exceptionhandler(interaction, message=None):
    if message:
        await interaction.author.send(message)
    elif hasattr(interaction, 'author'):
        await interaction.author.send(MESSAGE_D + str(traceback.format_exc()))
    else:
        await interaction.user.send(MESSAGE_D + str(traceback.format_exc()))


# This event is triggered for every message that the bot can see
COMMANDS = ["tbt"]
REPLY_DELETE = ['delete', 'd']
REPLY_COMMENT = ['comment', '#']
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

                elif message.attachments:
                    c = message.attachments[0].filename.lower()[:-4]
                    if c in COMMANDS:
                        infras = seedtoinfras(interaction.content,
                                              eval(c + "_OPTIONS"))
                        await commandhelper(interaction, True, message.content,
                                            infras, eval(c + "_INFRAS0"), c)


# a helper is used for all slash commands
MESSAGE_PUBLISH = " (publish with _pub)"
async def commandhelper(interaction, _pub, _seed, infras, infras0, name):
    try:
        infras_seed = seedtoinfras(_seed, eval(name + "_OPTIONS"))
        infras = amendinfras(infras_seed, infras)
        infras = amendinfras(infras0, infras)  #fallback
        infras = typedrive(infras, infras0)
        infrastofile_PIL(infras, name, eval(name + "_EXE"))
        _seed = infrastoseed(infras)
        with open(name + ".png", 'rb') as f:
            if hasattr(interaction, 'response'):
                await interaction.response.send_message(
                    _seed if _pub == True else _seed + MESSAGE_PUBLISH,
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
        size = pilmoji.getsize(textwrap, font=font)
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
    try:
        PILdraw.rectangle([(xyxy[0], xyxy[1]), (xyxy[2], xyxy[3])],
                          width=LINE_WIDTH,
                          fill=FONT_COLOR)
    except ValueError:  # when where line starts > where line ends
        pass


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
        wrappedtext = getwrappedtext_PIL(_texts[i], f_linearsizeref(spanmax), PILfont)
        multilinevector = f_mul(gettextsize(wrappedtext), multilinevector)
        return (singlelineanchor, wrappedtext, multilinevector)

    def getlineposture(postureparam):
        return f_mul(gettextsize(postureparam[0]), postureparam[1])

    # micros
    def f_linearsizeref(ref):
        (base, scale) = ref
        return infras[-1][base] * scale

    def f_max(l1, l2):
        return [max(a, b) for a, b in zip(l1, l2)]
    
    def f_add(l1, l2):
        return [l1[i] + l2[i] for i in range(len(l1))]

    def f_mul(l1, l2):
        return [l1[i] * l2[i] for i in range(len(l1))]

    
    
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
            f_max(_EXE_runtime[-1]['xy_principle'], srcimage.size), _fontsize)
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





####    diagram commons START ####

COMMAND_DESCRIPTION_COMMON = {
    "_pub": "sets if channel sees the bot's reply (default is False)",
    "_seed": "syntax: 1 foo" + SEED_DELIM_INFRA + " 2 bar" + SEED_DELIM_INFRA +
        " fontsize baz ... in which 1, 2 etc. are command options without prefix",
    "_tw": "tile width, which is the left-right unit distance between labels",
    "_th": "tile height, which is the bottom-up unit distance between labels",
    "_fs": "font size"
}

def getoptions(DESCRIPTIONS):
    return [
        [key.lstrip('_') for key in DESCRIPTIONS.keys()],
        [key.lstrip('_') for key in list(COMMAND_DESCRIPTION_COMMON.keys())[2:]]
    ]


####    diagram commons END ####




####    tbt START ####

tbt_NAME = "tbt"

tbt_DESCRIPTIONS = {
    "_1": "top right",
    "_2": "top left",
    "_3": "bottom left",
    "_4": "bottom right",
    "_xp": "when x is + (right)",
    "_xn": "when x is - (left)",
    "_yp": "when y is + (up)",
    "_yn": "when y is - (down)",
    "_x": "x axis label",
    "_y": "y axis label",
    "_t": "tbt title",
}

tbt_OPTIONS = getoptions(tbt_DESCRIPTIONS)

tbt_INFRAS0 = [[''] * 11, [200, 200, 24]]

tbt_EXE = [
    {'mode': 'text', 'position': (3, 1), 'posture': [(0, 2), 'mm', (0, -1/4)]},
    {'mode': 'text', 'position': (1, 1), 'posture': [(0, 2), 'mm', (0, -1/4)]},
    {'mode': 'text', 'position': (1, 3), 'posture': [(0, 2), 'mm', (0, -1/4)]},
    {'mode': 'text', 'position': (3, 3), 'posture': [(0, 2), 'mm', (0, -1/4)]},
    {'mode': 'text', 'position': (4, 2), 'posture': [(0, 2), 'rm', (0, -1/4)]},
    {'mode': 'text', 'position': (0, 2), 'posture': [(0, 2), 'lm', (0, -1/4)]},
    {'mode': 'text', 'position': (2, 0), 'posture': [(0, 2), 'ma', (0, 0)]},
    {'mode': 'text', 'position': (2, 4), 'posture': [(0, 2), 'md', (0, 0)]},
    {'mode': 'text', 'position': (3, 2), 'posture': [(0, 1), 'ra', (0, 0)]},
    {'mode': 'text', 'position': (2, 1), 'posture': [(0, .5), 'ra', (0, 0)]},
    {'mode': 'text', 'position': (0, 0), 'posture': [(0, 2), 'la', (0, 0)]},
    {'mode': 'line', 'position': [(0, 2), (4, 2)], 'posture': [(5, [1, 0]), (4, [-1, 0])]},
    {'mode': 'line', 'position': [(2, 0), (2, 4)], 'posture': [(6, [0, 1]), (7, [0, -1])]}
]


@bot.tree.command(name=tbt_NAME)
@app_commands.describe(**COMMAND_DESCRIPTION_COMMON, **tbt_DESCRIPTIONS)
async def tbt(interaction: discord.Interaction,
              _pub: bool = False,
              _seed: str = None,
              _1: str = None,
              _2: str = None,
              _3: str = None,
              _4: str = None,
              _xp: str = None,
              _xn: str = None,
              _yp: str = None,
              _yn: str = None,
              _x: str = None,
              _y: str = None,
              _t: str = None,
              _tw: int = None,
              _th: int = None,
              _fs: int = None):

    infras = [[_1, _2, _3, _4, _xp, _xn, _yp, _yn, _x, _y, _t],
              [_tw, _th, _fs]]

    await commandhelper(interaction, _pub, _seed, infras, tbt_INFRAS0,
                        tbt_NAME)

####    tbt END ####



####    rankedcut START ####



####    rankedcut END ####



bot.run(TOKEN)
