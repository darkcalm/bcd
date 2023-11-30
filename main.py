####	data structures processing START ####

import re

HASH_DELIM_SUPRA = '//'
HASH_DELIM_INFRA = ';'

async def INFRA_REGEX(param_name):
    return r"^(" + re.escape(
        param_name
    ) + ") ([^" + HASH_DELIM_INFRA + "]*)|" + HASH_DELIM_INFRA + " *(" + re.escape(
        param_name
    ) + ") ([^" + HASH_DELIM_INFRA + "]*)[" + HASH_DELIM_INFRA + " ]*"  # ^(1) ([^;]*)|; *(1) ([^;]*)[; ]*

async def amendinfras(oldinfras, newinfras):
    if not (oldinfras and newinfras):
        return oldinfras or newinfras
    for i, section in enumerate(newinfras):
        for j, new_value in enumerate(section):
            if new_value == None:
                newinfras[i][j] = oldinfras[i][j]
    return newinfras


async def infrastohash(infras):
    _hash = ""
    for i, section in enumerate(infras):
        for j, value in enumerate(section):
            if value is not None:
                _hash += str(value)
            _hash += HASH_DELIM_INFRA
        _hash = _hash[:-len(HASH_DELIM_INFRA)]
        _hash += HASH_DELIM_SUPRA
    _hash = _hash[:-len(HASH_DELIM_SUPRA)]
    return _hash


INFRA_VALUE_GROUPNUM = [1, 3]
INFRA_KEY_GROUPNUM = [0, 2]

async def hashtoinfras(_hash, _OPTIONS):
    if _hash is None:
        return None

    # assume a strict compact form first
    infras = _hash.split(HASH_DELIM_SUPRA)
    if len(infras) == len(_OPTIONS):
        for i, sections in enumerate(_OPTIONS):
            infras[i] = infras[i].split(HASH_DELIM_INFRA)
            if len(infras[i]) != len(sections):
                break;

    if len(infras) == len(_OPTIONS):
        return infras
        
    _hash = _hash.replace(HASH_DELIM_SUPRA, HASH_DELIM_INFRA)

    # parse and categorize input to parameters and image preferences
    match_bitmap = []
    match_result = []
    infras = []
    for i, section_params in enumerate(_OPTIONS):
        match_result.append([])
        infras.append([])

        for key in section_params:
            match_result[i].append(re.findall(await INFRA_REGEX(key),
                                              _hash))
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

async def typedrive(infras, infras0):
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

# Create the bot object.
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
                        infras = await hashtoinfras(interaction.content, eval(c + "_OPTIONS"))
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
async def commandhelper(interaction, _pub, _hash, infras, infras0, name):
    try:
        infras_hash = await hashtoinfras(_hash, eval(name + "_OPTIONS"))
        infras = await amendinfras(infras_hash, infras)
        infras = await amendinfras(infras0, infras)  #fallback
        infras = await typedrive(infras, infras0)
        await eval(name + "_tofile")(infras)
        _hash = await infrastohash(infras)
        with open(name + ".png", 'rb') as f:
            if hasattr(interaction, 'response'):
                await interaction.response.send_message(
                    _hash if _pub == True else _hash + MESSAGE_PUBLISH,
                    file=discord.File(f), ephemeral=not _pub)
            else:
                await interaction.channel.send(_hash, file=discord.File(f))
    
    except Exception:
        await exceptionhandler(interaction)

####    discord END ####




####	PIL START ####

from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

global BACKGROUND_COLOR, FONT_COLOR, LINE_WIDTH, FITS

BACKGROUND_COLOR = (255, 255, 255)
FONT_COLOR = (0, 0, 0)
LINE_WIDTH = 1

async def getPILresources(fontsize, width, height):    
    font = ImageFont.truetype('OpenSansEmoji.ttf', fontsize)
    PILimage = Image.new('RGB', (width, height),
                         color=BACKGROUND_COLOR)
    PILdraw = ImageDraw.Draw(PILimage)
    return PILimage, PILdraw, font


async def line_PIL(xyxy, PILdraw):
    try:
        PILdraw.rectangle([(xyxy[0], xyxy[1]),
                           (xyxy[2], xyxy[3])],
                          width=LINE_WIDTH,
                          fill=FONT_COLOR)
    except ValueError:
        pass


async def text_PIL(xy, text, wrapspan, anchor, font, PILimage):

    def getspan(target, font):
        return font.getbbox(target)[2]
        
    def getdist(target, font):
        return font.getbbox(target)[3]

    def appendwrap(text):
        lineDists.append(getdist(text, font))
        lineSpans.append(getspan(text, font))
        wrappedLines.append(text)
    
    # Initialize lists to hold the wrapped lines and their heights
    wrappedLines = []
    lineDists = []
    lineSpans = []

    span = 0
    lasti = 0
    for i in range(len(text)):
        if text[i:i+2] == '\\n':
            appendwrap(text[lasti:i].strip("\n"))
            lasti = i + 2
            span = 0

        elif span + getspan(text[i], font) < wrapspan:
            span += getspan(text[i], font)

        else:
            # wrap through a single-word line
            span = 0
            if len(text[lasti:i].strip(" ").split(" ")) < 2:
                appendwrap(text[lasti:i].strip(" "))
                lasti = i
            # wrap through a multi-word line
            else:
                append = " ".join(text[lasti:i].strip(" ").split(" ")[:-1])
                appendwrap(append)
                lasti = lasti + len(append) + 1
    appendwrap(text[lasti:].strip(" "))

    wrappedLines = "\n".join(wrappedLines)

    # anchors: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
    with Pilmoji(PILimage) as pilmoji:
        pilmoji.text(xy,
                     anchor = anchor,
                     text = wrappedLines,
                     font = font,
                     fill = FONT_COLOR)
        size = pilmoji.getsize(wrappedLines, font=font)
        return (size[0], size[1] + font.getmetrics()[1])
        # descent: https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd
         
        
####	PIL END ####






####    diagram commons START ####

COMMAND_DESCRIPTION_COMMON = {
    "_pub": "sets if channel sees the bot's reply (default is False)",
    "_hash": "syntax: 1 foo" + HASH_DELIM_INFRA + " 2 bar" + HASH_DELIM_INFRA + " fontsize baz ... in which 1, 2 etc. are command options without prefix",
    "_fs": "font size",
    "_w": "width",
    "_h": "height",
}

def _node(base, n, d, bias=0):
    return base * n / d + bias

####    diagram commons END ####


####	 tbt START ####

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

tbt_OPTIONS = [
    [key.lstrip('_') for key in tbt_DESCRIPTIONS.keys()],
    [key.lstrip('_') for key in list(COMMAND_DESCRIPTION_COMMON.keys())[2:]],
]

tbt_INFRAS0 = [[''] * 11, [42, 800, 800]]

tbt_EXE = [
    [(3, 1), (1, .5), 'mm'], [(1, 1), (1, .5), 'mm'], [(1, 3), (1, .5), 'mm'], [(3, 3), (1, .5), 'mm'], [(4, 2), (1, .5), 'rm'], [(0, 2), (1, .5), 'lm'], [(2, 0), (1, .5), 'ma'], [(2, 4), (1, .5), 'md'], [(3, 2), (1, .1), 'ma'], [(2, 1), (2, .1), 'ra'], [(0, 0), (1, .2), 'la']
]

async def tbt_tofile(infras):
    # notice the infras[-i]. this is to maintain body-head structures. in diagrams we don't think of diagram settings as primary to diagram content.
    PILimage, PILdraw, font = await getPILresources(infras[-1][0], infras[-1][1], infras[-1][2])

    # interfaces
    async def text(xy, text, wrapspan, anchor, font=font):
        if (text):
            return await text_PIL(
                xy, str(text), wrapspan, anchor, font, PILimage)

    async def line(xyxy, dependency):
        if (dependency):
            await line_PIL(xyxy, PILdraw)

    # macros
    def f_pos(xycoordinates, bx=0, by=0):
        (x, y) = xycoordinates
        return (_node(infras[-1][1], x, 4, bx),
                _node(infras[-1][2], y, 4, by))

    def f_wrapspan(basescale, textmargin=0):
        (b, s) = basescale
        return _node(infras[-1][b], s, 1, textmargin)

    def f_logic_any(list):
        return any([infras[-2][i] for i in list])
    
    # execution
    b = []
    for i, _ in enumerate(tbt_EXE):
        b.append (await text(f_pos(_[0]), infras[0][i], f_wrapspan(_[1]), _[2]))

    await line(f_pos((0, 2), bx=b[5][0]) + f_pos((4, 2), bx=-b[4][0]), f_logic_any([4, 5, 8]))
    await line(f_pos((2, 0), by=b[6][1]) + f_pos((2, 4), by=-b[7][1]), f_logic_any([6, 7, 9]))

    PILimage.save('tbt.png')


####	tbt constants and helpers END ####


@bot.tree.command(name='tbt')
@app_commands.describe(**COMMAND_DESCRIPTION_COMMON, **tbt_DESCRIPTIONS)
async def tbt(interaction: discord.Interaction,
              _pub: bool = False,
              _hash: str = None,
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

    await commandhelper(interaction, _pub, _hash, infras, tbt_INFRAS0, 'tbt')


####	 tbt END ####

bot.run(TOKEN)
