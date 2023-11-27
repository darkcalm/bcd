####	hashing helpers START ####

import re

HASH_DELIM_SUPRA = '//'
HASH_DELIM_INFRA = ';'

DESCRIPTION_PUB = "set to True, everyone sees the bot's reply (default is False)"
DESCRIPTION_HASH = "syntax: 1 foo"+HASH_DELIM_INFRA+" 2 bar" + HASH_DELIM_SUPRA + " fontsize baz; ..., in which 1, 2 etc. are command options without prefix"

SYNTAX_OR_BUG = "incorrect syntax ... or a bug?"

async def INFRA_REGEX(param_name):
	return r"^("+re.escape(param_name)+") ([^"+HASH_DELIM_INFRA+"]*)|"+HASH_DELIM_INFRA+" *("+re.escape(param_name)+") ([^"+HASH_DELIM_INFRA+"]*)["+HASH_DELIM_INFRA+" ]*" # ^(1) ([^;]*)|; *(1) ([^;]*)[; ]*

async def typedispatchloose(x, type:str):
	try:
		if type == "str":
			return str(x)
		if type == "int":
			return int(x)
	except ValueError:
		return x

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

async def hashtoinfrasstrict(_hash):
	infras = []
	for i, section in enumerate(_hash.split(HASH_DELIM_SUPRA)):
		infras.append(section.split(HASH_DELIM_INFRA))
		for j, value in enumerate(infras[i]):
			if value == '':
				infras[i][j] = None
	return infras

async def hashtoinfrasloose(_hash, _OPTIONS):
	if _hash is None:
		return None

	_hash = _hash.replace(HASH_DELIM_SUPRA, HASH_DELIM_INFRA)
	
	# parse and categorize input to parameters and image preferences
	match_bitmap = []
	match_result = []
	infras = []

	for i, section_params in enumerate(_OPTIONS):
		match_result.append([])
		infras.append([])

		for key in section_params:
			key = key.split(":")
			match_result[i].append(re.findall(await INFRA_REGEX(key[0]), _hash))
			infras[i].append([])

		for j, key in enumerate(section_params):
			if match_result[i][j] != []:
				infras[i][j] = await typedispatchloose(match_result[i][j][-1][INFRA_VALUE_GROUPNUM[0]] or match_result[i][j][-1][INFRA_VALUE_GROUPNUM[1]], key.split(":")[1])
			else:
				infras[i][j] = None

		match_bitmap.append(match_result[i] != [[]]*len(section_params))

	if match_bitmap == [False]*len(_OPTIONS):
		return False

	return infras

#### hashing helpers END ####




####	PIL interface and helpers START ####

from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji

global WIDTH, HEIGHT, BACKGROUND_COLOR, FONT_COLOR, LINE_WIDTH, FITS

WIDTH, HEIGHT = 800, 800
BACKGROUND_COLOR = (255,255,255)
FONT_COLOR = (0,0,0)

async def typedispatchstrict(x):
	try:
		return int(x)
	except ValueError:
		return 'error'

LINE_WIDTH = 1
FITS = [1, 0.8]

async def getPILresources(fontsize, margin):
	font = ImageFont.truetype('OpenSansEmoji.ttf', fontsize)
	font90 = ImageFont.TransposedFont(font, Image.ROTATE_90)	
	PILimage = Image.new('RGB', (WIDTH+2*margin, HEIGHT+2*margin), color=BACKGROUND_COLOR)
	PILdraw = ImageDraw.Draw(PILimage)
	return PILimage, PILdraw, font, font90

async def getw(target, font):
	return font.getbbox(target)[2]
	
async def geth(target, font):
	return font.getbbox(target)[3]

async def line_PIL(xyxy, margin, PILdraw):
	PILdraw.rectangle(
		[(xyxy[0]+margin,xyxy[1]+margin), (xyxy[2]+margin,xyxy[3]+margin)],
		width=LINE_WIDTH, fill=FONT_COLOR)

async def text_PIL(xy, text, wrapWidth, anchor, font, margin, PILimage):
	async def text_PIL_base(xy, text, font, margin):
		with Pilmoji(PILimage) as pilmoji:
			pilmoji.text(
				(int(xy[0])+margin, int(xy[1])+margin),
				text, font=font, fill=FONT_COLOR)
	
	# Initialize lists to hold the wrapped lines and their heights
	wrappedLines = []
	lineHeights = []
	async def appendwrap(text):
		wrappedLines.append(text)
		lineHeights.append(await geth(text, font))

	accumulatedWidth = 0
	lasti = 0
	for i in range(len(text)):
		
		if text[i] == '\n':
			await appendwrap(text[lasti:i].strip("\n").strip(" "))
			await appendwrap('\n')
			lasti = i + 1
			accumulatedWidth = 0
			
		elif accumulatedWidth + await getw(text[i], font) < wrapWidth:
			accumulatedWidth += await getw(text[i], font)
			
		else:
			# If there's only one word on the line, wrap the line before this character
			accumulatedWidth = 0
			if len(text[lasti:i].strip(" ").split(" ")) < 2:
				await appendwrap(text[lasti:i].strip(" "))
				lasti = i
			# Otherwise, wrap the line at the last space
			else:
				append = " ".join(text[lasti:i].strip(" ").split(" ")[:-1])
				await appendwrap(append)
				lasti = lasti + len(append) + 1
	# Append any remaining text to the wrap list
	await appendwrap(text[lasti:].strip(" "))

	# Note the peculiarity in font90 involves lineHeights
	totalheight = sum(lineHeights)
	x, y = {'h-': xy,
					'h0': (xy[0], xy[1] - totalheight/2),
					'h+': (xy[0], xy[1] - totalheight),
					'v-': (xy[0] + lineHeights[0]/2, xy[1]),
					'v0': (xy[0] - totalheight/2, xy[1]),
					'v+': (xy[0] - totalheight - lineHeights[-1]/2, xy[1])
				 } [anchor[0] + anchor[2]]
	
	# Determine and draw each line of text at the appropriate position based on the anchor parameter
	for i in range(len(wrappedLines)):
		await text_PIL_base({
			'h+': (x, y + sum(lineHeights[:i])),
			'h0': (x - await getw(wrappedLines[i], font)/2,
						 y + sum(lineHeights[:i])),
			'h-': (x - await getw(wrappedLines[i], font),
						 y + sum(lineHeights[:i])),
			'v+': (x + sum(lineHeights[:i]),
						 y - await getw(wrappedLines[i], font)),
			'v0': (x + sum(lineHeights[:i]), 
						 y- await getw(wrappedLines[i], font)/2),
			'v-': (x + sum(lineHeights[:i]), y)
			} [anchor[0] + anchor[1]], wrappedLines[i], font, margin)
	pass

####	PIL interface and helpers END ####




####	tbt constants and helpers START ####

tbt_OPTIONS = [
	['1:str','2:str','3:str','4:str','xp:str','xn:str','yp:str','xn:str','x:str','y:str','t:str'],
	['fontsize:int', 'margin:int']]

async def tbt_tofile(infras):
	infras[1] = [await typedispatchstrict(item) for item in infras[1]]
	if any(item == "error" for item in infras[1]):
		return False

	PILimage, PILdraw, font, font90 = await getPILresources(infras[1][0], infras[1][1])

	# interfaces
	async def text(xy, text, wrapWidth, anchor, font=font):
		if (text):
			await text_PIL(xy, str(text), wrapWidth, anchor, font90 if anchor[0]=="v" else font, infras[1][1], PILimage)

	async def line(xyxy, dependency):
		if (dependency):
			await line_PIL(xyxy, infras[1][1], PILdraw)
	
	# macros
	def C44(x, y):
		return (CW(x, 4), CH(y, 4))

	def FD2(fit, dir):
		return FITS[fit]*dir(1,2)

	def DANY(list):
		return any([infras[0][i] for i in list])

	# micros
	def CW(n, d):
		return WIDTH*n/d

	def CH(n, d):
		return HEIGHT*n/d
	
	# executions
	await text(C44(3,1), infras[0][0], FD2(1,CW), 'h00')
	await text(C44(1,1), infras[0][1], FD2(1,CW), 'h00')
	await text(C44(1,3), infras[0][2], FD2(1,CW), 'h00')
	await text(C44(3,3), infras[0][3], FD2(1,CW), 'h00')
	await text(C44(4,2), infras[0][4], FD2(1,CW), 'h-+')
	await text(C44(0,2), infras[0][5], FD2(1,CW), 'h++')
	await text(C44(2,0), infras[0][6], FD2(1,CW), 'h+-')
	await text(C44(2,4), infras[0][7], FD2(1,CW), 'h-+')
	await text(C44(3,2), infras[0][8], FD2(0,CW), 'h0-')
	await text(C44(2,1), infras[0][9], FD2(0,CH), 'v0+')
	await text(C44(0,0), infras[0][10], FD2(1,CW), 'h+-')
	await line(C44(0,2)+C44(4,2), DANY([5,7,8]))
	await line(C44(2,0)+C44(2,4), DANY([4,6,9]))

	PILimage.save('tbt.png')

####	tbt constants and helpers END ####




####	rankedcut constants and helpers START ####

####	rankedcut constants and helpers END ####





####	 discord interfaces and helpers START ####

import os, traceback

import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.environ['DISCORD_BOT_TOKEN']

MESSAGE_PUBLISH = " (publish with _pub)"
MESSAGE_DEV = "got a system message 🤖️ contact the developer with:\n\n"
MESSAGE_FILENAME = "file name should be a diagram type ex. tbt.png"
MESSAGE_TYPE = "type error in the option ex. gave string instead of int"

COMMAND_DESCRIPTION_COMMON = {
	"_pub": DESCRIPTION_PUB, "_hash": DESCRIPTION_HASH,
	"_fontsize": "font size", "_margin": "margin"
}

# Create the bot object.
bot = commands.Bot(command_prefix='/',intents=discord.Intents.default())

@bot.event
async def on_ready():
	try:
		synced = await bot.tree.sync()
		print(f"synced {len(synced)} command(s)")
	except Exception as e:
		print(e)

# A handler is used for ongoing events
async def exceptionhandler(interaction):
	if hasattr(interaction, 'author'):
		await interaction.author.send(
			MESSAGE_DEV + str(traceback.format_exc())
		)
	else:
		await interaction.user.send(
			MESSAGE_DEV + str(traceback.format_exc())
		)

# This event is triggered for every message that the bot can see
DIAGRAM_COMMANDS = ["tbt"]
DELETION = ['delete', 'd']
@bot.event
async def on_message(interaction):
	if interaction.author.id == bot.user.id:
		return

	# If the message is a reply and it's in a channel
	if interaction.reference and interaction.channel:
		# Fetch the message that was replied to
		message = await interaction.channel.fetch_message(
			interaction.reference.message_id
		)
		if hasattr(message, 'author'):
			if message.author.id == bot.user.id:
				if interaction.content in DELETION:
					await message.delete()

				else:
					try:
						if message.attachments:
							if message.attachments[0].filename.lower().endswith('.png'):
								diagram = str(message.attachments[0].filename).split('.')
								
								if diagram[0] in DIAGRAM_COMMANDS:
									oldinfras = await hashtoinfrasstrict(
										message.content)
									newinfras = await hashtoinfrasloose(
										interaction.content, eval(diagram[0]+"_OPTIONS"))

									if newinfras == False:
										await interaction.author.send(
											DESCRIPTION_HASH)

									else:
										infras = await amendinfras(oldinfras, newinfras)
										tofile = await eval(diagram[0]+"_tofile")(infras)
										if tofile == False:
											await interaction.author.send(MESSAGE_TYPE)
										
										with open(diagram[0]+'.png', 'rb') as f:
											await interaction.channel.send(
												await infrastohash(infras), file = discord.File(f)
											)	
										
								else:
									await interaction.author.send(MESSAGE_FILENAME)
							else:
								pass
						else:
							pass
					except Exception:
						await exceptionhandler(interaction)
						
			else:
				pass

# A helper is used for all slash commands
async def commandhelper(interaction, _pub, _hash, infras, infras0, name):
	try:	
		infras_hash = await hashtoinfrasloose(_hash, eval(name+"_OPTIONS"))
		if infras_hash == False:
			await interaction.response.send_message(SYNTAX_OR_BUG + DESCRIPTION_HASH, ephemeral = True)
		
		infras = await amendinfras(infras_hash, infras)
		infras = await amendinfras(infras0, infras) #fallback
		
		tofile = await eval(name+"_tofile")(infras)
		if tofile == False:
			await interaction.author.send(MESSAGE_TYPE)
	
		_hash = await infrastohash(infras)
		with open(name+".png", 'rb') as f:
			await interaction.response.send_message(
				_hash if _pub == True else _hash + MESSAGE_PUBLISH,
				file = discord.File(f),
				ephemeral = not _pub
			)

	except Exception:
		await exceptionhandler(interaction)
	
####	 interfaces of helper for discord END ####






####	 slash commands START ####


tbt_DESCRIPTIONS = {
	"_1": "1st quadrant",
	"_2": "2nd quadrant",
	"_3": "3rd quadrant",
	"_4": "4th quadrant",
	"_xp": "when x is + (right)",
	"_xn": "when x is - (left)",
	"_yp": "when y is + (up)",
	"_yn": "when y is - (down)",
	"_x": "x axis label",
	"_y": "y axis label",
	"_t": "tbt title",
}

@bot.tree.command(name='tbt')
@app_commands.describe(**COMMAND_DESCRIPTION_COMMON,**tbt_DESCRIPTIONS)
async def tbt(
	interaction:discord.Interaction,
	_pub:bool=False,
	_hash:str=None,
							_1:str=None,_2:str=None,_3:str=None,_4:str=None,_xp:str=None,_xn:str=None,_yp:str=None,_yn:str=None,_x:str=None,_y:str=None,_t:str=None,
	_fontsize:int=None,_margin:int=None):

	infras = [
		[_1, _2, _3, _4, _xp, _xn, _yp, _yn, _x, _y, _t],
		[_fontsize, _margin]
	]

	infras0 = [[None]*11,[42, 84]]
	
	await commandhelper(interaction, _pub, _hash, infras, infras0, 'tbt')

####	 slash commands END ####






bot.run(TOKEN)