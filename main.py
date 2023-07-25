import discord
from discord import app_commands
from discord.ext import commands

import PIL # Potential hotfix: font.size if hasattr(font,'size') else font.font.size
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji  # Allows for handling of emojis in the image creation process
import emoji

# Retrieves bot and OpenAI API keys from environment variables.
import os
import openai
import asyncio

import re
import math

TOKEN = os.environ['DISCORD_BOT_TOKEN']
openai.api_key = os.environ['OPENAI_API_KEY']

# Various constants used throughout the bot's functionality.
PARAM_NUM = 11
HASH_DELIM = '.:.'
REPLY_DELIM = ','
BREAK_DELIM = '\n'
DELETION = ['delete', 'd']
PARAM_OPTIONS = [
	'_1','_2','_3','_4','_yp','_xn','_yn','_xp','_x','_y','_t',
	'1','2','3','4','yp','xn','yn','xp','x','y','t',
] # This uses the % operator to assign values to the parameters
FONT_SIZE_REGEX = r"^font (\d+)(,)*(.*)$"
MARGIN_REGEX = r"^margin (\d+)(,)*(.*)$"

# Function to reset various image-related parameters.
def reset_parameters():
	global LINE_WIDTH, WIDEFIT, MIDFIT, BACKGROUND_COLOR, FONT_COLOR, FONT_SIZE, MARGIN
	LINE_WIDTH = 1
	WIDEFIT = 1
	MIDFIT = 0.8
	BACKGROUND_COLOR = (255,255,255)
	FONT_COLOR = (0,0,0)
	FONT_SIZE = 24
	MARGIN = 84
reset_parameters()

# This function will convert a generic input, which currently may or may not include hash and other commands, into execute and returns a hash format
async def tohash(hash):
	if hash is None:
		return None

	# Check if the input matches the font size formatting pattern, if it does, update the global font size and modify the hash to continue
	match = re.match(FONT_SIZE_REGEX, hash)
	if match:
		global FONT_SIZE
		FONT_SIZE = int(match.group(1))
		hash = match.group(3) or HASH_DELIM*(PARAM_NUM-1)

	# ditto for margins
	match = re.match(MARGIN_REGEX, hash)
	if match:
		global MARGIN
		MARGIN = int(match.group(1))
		hash = match.group(3) or HASH_DELIM*(PARAM_NUM-1)
	
	# If there's only one part and it's correctly formatted as a hash and not a reply, return it
	cuts = hash.split(REPLY_DELIM)
	if len(cuts) == 1 and len(hash.split(HASH_DELIM)) > 1:
		if len(hash.split((HASH_DELIM))) == PARAM_NUM:
			return hash
		return False

	# Assuming the reply is formatted as a reply and not a hash, iterate over each part of the input
	processed = {}
	for cut in cuts:
		c = cut.strip(" ").split(" ")
		# If a cut is not properly spaced or the segment before the first space is not a valid paramter option, return False
		if len(c) == 1 or c[0] not in PARAM_OPTIONS:
			return False
		else:
			key = PARAM_OPTIONS.index(c[0]) % PARAM_NUM
			# If the key already exists, append the rest of the segment on the next line, if it doesn't exist, create a new entry
			if key in processed.keys():
				processed[key] += BREAK_DELIM + " ".join(c[1:])
			else:
				processed[key] = " ".join(c[1:])

	# Reconstruct the final hash from the processed inputs
	hash = ""
	keys = list(processed.keys())
	values = list(processed.values())
	for i in range(PARAM_NUM):
		if i in processed.keys():
			hash += values[keys.index(i)]
		if i != PARAM_NUM - 1:
			hash += HASH_DELIM
	
	return hash

# If a corresponding item in hash2 is empty, it is assigned with the item from hash
async def amendhash(hash=None, newhash=None):
	if newhash == None:
		return hash
	if hash == None:
		return newhash
		
	newhash = newhash.split(HASH_DELIM)	
	for i, keep in enumerate(hash.split(HASH_DELIM)):
		if newhash[i] == "":
			newhash[i] = keep
	return HASH_DELIM.join(newhash)

# This function will convert a hash into a diagram
async def tofile(hash:str=""):
	width, height = 800, 800
	image = Image.new('RGB', (width+2*MARGIN, height+2*MARGIN), color=BACKGROUND_COLOR)
	draw = ImageDraw.Draw(image)
	font = ImageFont.truetype('OpenSansEmoji.ttf', FONT_SIZE)
	font90 = ImageFont.TransposedFont(font, Image.ROTATE_90)

	def getw(target):
		return font.getlength(target)
	def geth(target):
		return font.getbbox(target)[3]

	
	def drawtextdefault(xy, text, font=font):
		with Pilmoji(image) as pilmoji:
			pilmoji.text((int(xy[0])+MARGIN, int(xy[1])+MARGIN), text, font=font, fill=FONT_COLOR)
			
	def drawline(xyxy):
		draw.line((xyxy[0]+MARGIN,xyxy[1]+MARGIN, xyxy[2]+MARGIN,xyxy[3]+MARGIN), fill=FONT_COLOR)


	def drawellipse(xyr): #unused
		r = int(math.sqrt((xyr[0]-xyr[2])**2 + (xyr[1]-xyr[3])**2))
		xyxy = (xyr[0] - r, xyr[1] - r, xyr[0] + r, xyr[1] + r)
		draw.ellipse(xyxy, outline=FONT_COLOR)

	
	# This function is used to draw text onto the image, handling automatic line wrapping, alignment, and positioning.
	def drawprose(xy, text, wrapWidth, anchor, font=font):
		# Initialize lists to hold the wrapped lines and their heights
		wrappedLines = []
		lineHeights = []
		def appendwrap(text):
			wrappedLines.append(text)
			lineHeights.append(geth(text))

		accumulatedWidth = 0
		lasti = 0
		for i in range(len(text)):
			# If the current character is a newline, wrap the line here
			if text[i] == '\n':
				appendwrap(text[lasti:i].strip("\n").strip(" "))
				appendwrap('\n')
				lasti = i + 1
				accumulatedWidth = 0
			# If the size of the current line plus the width of the next character is less than the wrap size, add the character to the line
			elif accumulatedWidth + getw(text[i]) < wrapWidth:
				accumulatedWidth += getw(text[i])
			else:
				# If there's only one word on the line, wrap the line before this character
				accumulatedWidth = 0
				if len(text[lasti:i].strip(" ").split(" ")) < 2:
					appendwrap(text[lasti:i].strip(" "))
					lasti = i
				# Otherwise, wrap the line at the last space
				else:
					append = " ".join(text[lasti:i].strip(" ").split(" ")[:-1])
					appendwrap(append)
					lasti = lasti + len(append) + 1
		# Append any remaining text to the wrap list
		appendwrap(text[lasti:].strip(" "))

		# Determine the starting x and y coordinates for the text based on the anchor parameter
		totalheight = sum(lineHeights)
		x, y = {'h-': xy,
						'h0': (xy[0], xy[1] - totalheight/2),
						'h+': (xy[0], xy[1] - totalheight),
						'v-': xy,
						'v0': (xy[0] - totalheight/2, xy[1]),
						'v+': (xy[0] - totalheight, xy[1])
					 } [anchor[0] + anchor[2]]

		# Determine and draw each line of text at the appropriate position based on the anchor parameter
		for i in range(len(wrappedLines)):
			drawtextdefault({
				'h+': (x, y + sum(lineHeights[:i])),
				'h0': (x - getw(wrappedLines[i])/2, y + sum(lineHeights[:i])),
				'h-': (x - getw(wrappedLines[i]), y + sum(lineHeights[:i])),
				'v+': (x + sum(lineHeights[:i]), y - getw(wrappedLines[i])),
				'v0': (x + sum(lineHeights[:i]), y - getw(wrappedLines[i])/2),
				'v-': (x + sum(lineHeights[:i]), y)
				} [anchor[0] + anchor[1]], wrappedLines[i], font=font)
		pass
	
	# Setting the canvas dimensions and calculating some key coordinates
	[_1, _2, _3, _4, _yp, _xn, _yn, _xp, _x, _y, _t] = hash.split(HASH_DELIM)
	ox = width/2
	oy = height/2
	q1x = ox + (width-ox)/2
	q1y = oy - (height-oy)/2
	q2x = ox - (width-ox)/2
	q2y = q1y
	q3x = q2x
	q3y = oy + (height-oy)/2
	q4x = q1x
	q4y = q3y

	drawprose((q1x, q1y), _1, (width-ox) * MIDFIT, 'h00')
	drawprose((q2x, q2y), _2, (ox) * MIDFIT, 'h00')
	drawprose((q3x, q3y), _3, (ox) * MIDFIT, 'h00')
	drawprose((q4x, q4y), _4, (width-ox) * MIDFIT, 'h00')

	if (_yp != ''):
		drawline((ox - LINE_WIDTH/2, 0, ox - LINE_WIDTH/2, oy))
		drawprose((ox, 0), _yp, (width-ox) * MIDFIT, 'h+-')	
		
	if (_xn != ''):
		drawline((0, oy, ox - LINE_WIDTH/2, oy))
		drawprose((0, oy), _xn, ox * MIDFIT, 'h++')

	if (_yn != ''):
		drawline((ox - LINE_WIDTH/2, height, ox - LINE_WIDTH/2, oy))
		drawprose((ox, height), _yn, (width-ox) * MIDFIT, 'h++')
		
	if (_xp != ''):
		drawline((width, oy, ox - LINE_WIDTH/2, oy))
		drawprose((width, oy), _xp, (width-ox) * MIDFIT, 'h-+')
	
	if (_x != ''):
		drawline((0, oy, width, oy))
		drawprose((q1x, oy), _x, (width-ox) * WIDEFIT, 'h0-')
		
	if (_y!= ''):
		drawline((ox - LINE_WIDTH/2, 0, ox - LINE_WIDTH/2, height))
		drawprose((ox, q1y), _y, (oy) * WIDEFIT, 'v0+', font90)
	
	if (_t != ''):
		drawprose((0, 0), _t, ox * MIDFIT, 'h+-')
	
	image.save('diagram.png')

	reset_parameters()



# Create the bot object.
bot = commands.Bot(command_prefix='/',intents=discord.Intents.default())

# Called when the bot is ready and has logged in.
@bot.event
async def on_ready():
	try:
		synced = await bot.tree.sync()
		print(f"synced {len(synced)} command(s)")
	except Exception as e:
		print(e)

# This event is triggered for every message that the bot can see
@bot.event
async def on_message(interaction):
	# If the bot itself sent the message, do nothing.
	if interaction.author.id == bot.user.id:
		return

	# If the message is a reply and it's in a channel
	if interaction.reference and interaction.channel:
		# Fetch the message that was replied to
		target = await interaction.channel.fetch_message(
			interaction.reference.message_id
		)
		if hasattr(target, 'author'):
			# If the replied message was sent by the bot
			if target.author.id == bot.user.id:
				# If the content of the message is a delete command
				if interaction.content in DELETION:
					await target.delete()

				else:
					# Try to convert the message content to a hash, if the conversion failed, send a message with the correct syntax
					newhash = await tohash(interaction.content)
					if newhash == False:
						await interaction.author.send(
							"syntax: x label"+REPLY_DELIM+" y spaced label"
						)
					
					else:
						# Amend the hash of the target message and generate a diagram, send the amended hash and the generated diagram in a message
						hash = await amendhash(target.content, newhash)
						await tofile(hash)
						with open('diagram.png', 'rb') as f:
							await interaction.channel.send(
								hash,
								file = discord.File(f)
							)	
			else:
				pass

# Command that generates a diagram from a hash
@bot.tree.command(name='tbt')
@app_commands.describe(
	hash = "writing here with the format 🌇.:.🌄.:.🌌.:.🌃.::.🌞.:.🏞️.:.🌜.:.🏬.:.🗺️.:.⏱️.:.🥱 makes the graph directly",
	_1 = "1st quadrant",
	_2 = "2nd quadrant",
	_3 = "3rd quadrant",
	_4 = "4th quadrant",
	_yp = "when y is + (up)",
	_xn = "when x is - (left)",
	_yn = "when y is - (down)",
	_xp = "when x is + (right)",
	_x = "x coordinate",
	_y = "y coordinate",
	_t = "title of diagram",
	_pub = "True = publish, otherwise by default only you can see the bot reply"
)
async def tbt(interaction:discord.Interaction,
							hash:str=None,
								_1:str="",
								_2:str="",
								_3:str="",
								_4:str="",
								_yp:str="",
								_xn:str="",
								_yn:str="",
								_xp:str="",
								_x:str="",
								_y:str="",
								_t:str="",
							_pub:bool=False
						 	):
	try:
								
		hash = await tohash(hash)
		if hash == False:
			await interaction.response.send_message(
				"incorrect format ... or a bug?",
				ephemeral = True
			)
	
		else:
			hash = await amendhash(hash, HASH_DELIM.join([_1, _2, _3, _4, _yp, _xn, _yn, _xp, _x, _y, _t]))
			await tofile(hash)
			# send to discord
			with open('diagram.png', 'rb') as f:
				await interaction.response.send_message(
					hash if _pub == True else hash + " (publish with _pub)",
					file = discord.File(f),
					ephemeral = not _pub
				)

	except Exception as e:
		if hasattr(interaction, 'author'):
			await interaction.author.send(e)
		else:
			await interaction.user.send(e)
	






### under development: topology layer to generalize tofile()
@bot.tree.command(name='gram')
@app_commands.describe(s = 'building now')
async def gram(interaction:discord.Interaction, s:str=""):
	try:
		pass
		#matches = re.findall(, speak)

		#if not matches:
		#	await interaction.response.send_message(
		#		"incorrect format ... or a bug?",
		#		ephemeral = True
		#	)

		#matches = matches[0]
		
		#hash = ""
		
		#await tofile("")

		#with open('diagram.png', 'rb') as f:
		#	await interaction.response.send_message(
		#		hash, file = discord.File(f)
		#	)
	except Exception as e:
		if hasattr(interaction, 'author'):
			await interaction.author.send(e)
		else:
			await interaction.user.send(e)

bot.run(TOKEN)