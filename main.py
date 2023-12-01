####	data structures processing START ####

import re

SEED_DELIM_SUPRA = '//'
SEED_DELIM_INFRA = ';'

def INFRA_REGEX(param_name):
    return r"^(" + re.escape(
        param_name
    ) + ") ([^" + SEED_DELIM_INFRA + "]*)|" + SEED_DELIM_INFRA + " *(" + re.escape(
        param_name
    ) + ") ([^" + SEED_DELIM_INFRA + "]*)[" + SEED_DELIM_INFRA + " ]*"  # ^(1) ([^;]*)|; *(1) ([^;]*)[; ]*

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
            if value is not None:
                _seed += str(value)
            _seed += SEED_DELIM_INFRA
        _seed = _seed[:-len(SEED_DELIM_INFRA)]
        _seed += SEED_DELIM_SUPRA
    _seed = _seed[:-len(SEED_DELIM_SUPRA)]
    return _seed


INFRA_VALUE_GROUPNUM = [1, 3]
INFRA_KEY_GROUPNUM = [0, 2]

def seedtoinfras(_seed, _OPTIONS):
    if _seed is None:
        return None

    # assume a strict compact form first
    infras = _seed.split(SEED_DELIM_SUPRA)
    if len(infras) == len(_OPTIONS):
        for i, sections in enumerate(_OPTIONS):
            infras[i] = infras[i].split(SEED_DELIM_INFRA)
            if len(infras[i]) != len(sections):
                break;

    if len(infras) == len(_OPTIONS):
        return infras

    _seed = _seed.replace(SEED_DELIM_SUPRA, SEED_DELIM_INFRA)

    # parse and categorize input to parameters and image preferences
    match_bitmap = []
    match_result = []
    infras = []
    for i, section_params in enumerate(_OPTIONS):
        match_result.append([])
        infras.append([])

        for key in section_params:
            match_result[i].append(re.findall(INFRA_REGEX(key),
                                              _seed))
            infras[i].append([])

        for j, key in enumerate(section_params):
            if match_result[i][j] != []:
                infras[i][j] = match_result[i][j][-1][INFRA_VALUE_GROUPNUM[0]] or match_result[i][j][-1][INFRA_VALUE_GROUPNUM[1]]
            else:
                infras[i][j] = None

        match_bitmap.append(match_result[i] != [[]] * len(section_params))

    if match_bitmap == [False] * len(_OPTIONS):
        return False

    return infras

def typedrive(infras, infras0):
    for i, section in enumerate(infras0):
        for j, value in enumerate(section):
            if isinstance(value, int):
                infras[i][j] = int(float(infras[i][j]))
            elif isinstance(value, str):
                infras[i][j] = str(infras[i][j])
    return infras

####    data structures processing END ####



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
MESSAGE_D = "🤖️ bug or personal? check it out or contact dev with:\n\n"
async def exceptionhandler(interaction, message=None):
    if message:
        await interaction.author.send(message)
    elif hasattr(interaction, 'author'):
        await interaction.author.send(MESSAGE_D+str(traceback.format_exc()))
    else:
        await interaction.user.send(MESSAGE_D+str(traceback.format_exc()))

# This event is triggered for every message that the bot can see
COMMANDS = ["tbt"]
REPLY_DELETE = ['delete', 'd']
REPLY_COMMENT = ['comment', '#']
@bot.event
async def on_message(interaction):
    if interaction.author.id == bot.user.id:
        return

    # If the message is a reply and it's in a channel
    if interaction.reference and interaction.channel:
        message = await interaction.channel.fetch_message(interaction.reference.message_id)

        if hasattr(message, 'author'):
            if message.author.id == bot.user.id:
                if interaction.content in REPLY_DELETE:
                    await message.delete()

                elif interaction.content in REPLY_COMMENT:
                    pass

                elif message.attachments:
                    c = message.attachments[0].filename.lower()[:-4]
                    if c in COMMANDS:
                        infras = seedtoinfras(interaction.content, eval(c + "_OPTIONS"))
                        await commandhelper(
                            interaction,
                            True,
                            message.content,
                            infras,
                            eval(c+"_INFRAS0"),
                            c
                        )


# A helper is used for all slash commands
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
                    file=discord.File(f), ephemeral=not _pub)
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

def getresources_PIL(fontsize, width, height):    
    font = ImageFont.truetype('OpenSansEmoji.ttf', fontsize)
    PILimage = Image.new('RGB', (width, height),
                         color=BACKGROUND_COLOR)
    PILdraw = ImageDraw.Draw(PILimage)
    return PILimage, PILdraw, font

# descent: https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
def getsize_PIL(textwrap, font, PILimage):
    with Pilmoji(PILimage) as pilmoji:
        size = pilmoji.getsize(textwrap, font=font)
        return [size[0], size[1] + font.getmetrics()[1]]

# textwrap is a string with potentially more than 0 line breaks ("\n"). discord input strings shows \\n, so we replace it with \n, alongside other requirements of line change
def gettextwrap_PIL(text, wrapspan, font):
    def getspan(target, font):
        return font.getbbox(target)[2]

    def getdist(target, font):
        return font.getbbox(target)[3]

    textwrap = []
    span = 0
    lasti = 0
    for i in range(len(text)):
        if text[i:i+2] == '\\n':
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
        PILdraw.rectangle([(xyxy[0], xyxy[1]),
                           (xyxy[2], xyxy[3])],
                          width=LINE_WIDTH,
                          fill=FONT_COLOR)
    except ValueError: # when where line starts > where line ends
        pass

def text_PIL(xy, textwrap, anchor, font, PILimage):
    with Pilmoji(PILimage) as pilmoji:
        pilmoji.text(xy,
                     anchor = anchor,
                     text = textwrap,
                     font = font,
                     fill = FONT_COLOR)

def infrastofile_PIL(infras, name, _EXE):
    # notice the infras[-i]. this is to maintain body-head structures. in diagrams we don't think of diagram settings as primary to diagram content.
    PILimage, PILdraw, font = getresources_PIL(infras[-1][0], infras[-1][1], infras[-1][2])

    # interfaces
    def text(textwrap, anchor, xy):
        if (textwrap):
            return text_PIL(xy, textwrap, anchor, font, PILimage)

    def line(dependency, xyxy):
        if (dependency):
            line_PIL(xyxy, PILdraw)

    def gettextwrap(i):
        return gettextwrap_PIL(
            infras[-2][i], f_wrapspan(_EXE[i][1]), font)

    def gettextsize(i):
        return getsize_PIL(gettextwrap(i), font, PILimage)

    # macros

    def f_coordinates(xycoordinates, biasextents = (0,0), mode="cartesian4x4"):
        if mode == "cartesian4x4":
            (x, y, bx, by) = xycoordinates + biasextents
            return [f_linear(infras[-1][1], x, 4, bx),
                    f_linear(infras[-1][2], y, 4, by)]

    def f_wrapspan(baseandscale):
        return infras[-1][baseandscale[0]] * baseandscale[1]

    def f_anylabel(l):
        return any([infras[-2][i] for i in l])

    def f_add(l1, l2):
        return [l1[i] + l2[i] for i in range(len(l1))]

    def f_mul(l1, l2):
        return [l1[i] * l2[i] for i in range(len(l1))]

    def f_linear(base, n, d=1, bias=0):
        return base * n / d + bias

    # execution
    for i, _ in enumerate(_EXE):
        if _[0] == 'text':
            text(gettextwrap(i),  _[2], f_coordinates(_[3]))
        elif _[0] == 'line':
            line(f_anylabel(_[1]),
                 f_add(f_mul(gettextsize(_[2][0][0]), _[2][0][1]), f_coordinates(_[3][0])) + 
                 f_add(f_mul(gettextsize(_[2][1][0]), _[2][1][1]), f_coordinates(_[3][1])))

    PILimage.save(name + '.png')


####	PIL END ####






####    diagram commons START ####

COMMAND_DESCRIPTION_COMMON = {
    "_pub": "sets if channel sees the bot's reply (default is False)",
    "_seed": "syntax: 1 foo" + SEED_DELIM_INFRA + " 2 bar" + SEED_DELIM_INFRA + " fontsize baz ... in which 1, 2 etc. are command options without prefix",
    "_fs": "font size",
    "_w": "width",
    "_h": "height",
}

def getoptions(DESCRIPTIONS):
    return [
        [key.lstrip('_') for key in DESCRIPTIONS.keys()],
        [key.lstrip('_') for key in list(COMMAND_DESCRIPTION_COMMON.keys())[2:]],
    ]

####    diagram commons END ####


####	 tbt START ####

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

tbt_INFRAS0 = [[''] * 11, [42, 800, 800]]

tbt_EXE = [    # type -> posturing -> drop location
    ['text', (1, .5), 'mm', (3, 1)],
    ['text', (1, .5), 'mm', (1, 1)],
    ['text', (1, .5), 'mm', (1, 3)],
    ['text', (1, .5), 'mm', (3, 3)],
    ['text', (1, .5), 'rm', (4, 2)],
    ['text', (1, .5), 'lm', (0, 2)],
    ['text', (1, .5), 'ma', (2, 0)],
    ['text', (1, .5), 'md', (2, 4)],
    ['text', (1, .1), 'ma', (3, 2)],
    ['text', (2, .1), 'ra', (2, 1)],
    ['text', (1, .2), 'la', (0, 0)],
    ['line', [4, 5, 8], [(5,[1,0]), (4,[-1,0])], [(0, 2), (4, 2)]],
    ['line', [6, 7, 9], [(6,[0,1]), (7,[0,-1])], [(2, 0), (2, 4)]]
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
              _fs: int = None,
              _w: int = None,
              _h: int = None):

    infras = [[_1, _2, _3, _4, _xp, _xn, _yp, _yn, _x, _y, _t],
              [_fs, _w, _h]]

    await commandhelper(interaction, _pub, _seed, infras, tbt_INFRAS0, tbt_NAME)

####	 tbt END ####



bot.run(TOKEN)