import discord
from discord import app_commands
from discord.ext import commands
import PIL
from PIL import Image, ImageDraw, ImageFont
import os
import inspect

TOKEN = os.environ['your_bot_token_here']

PARAM_NUM = 11

HASH_DELIM = '.:.'

bot = commands.Bot(
	command_prefix='/',
	intents=discord.Intents.default()
)

@bot.event
async def on_ready():
	print('ready')
	try:
		synced = await bot.tree.sync()
		print(f"synced {len(synced)} command(s)")
	except Exception as e:
		print(e)

@bot.event
async def on_message(interaction):
	if interaction.author.id == bot.user.id:
		return

	if interaction.reference:
		replied = await interaction.channel.fetch_message(
			interaction.reference.message_id
		)
		if replied.author.id == bot.user.id:
			if interaction.content in ['delete', 'd']:
				await replied.delete()

			else:
				hash = await tohash(interaction.content)
				if hash == False:
					await interaction.author.send(
						"ex. x name, y name with space"
					)
				
				else:
					hash = await amendhash(replied.content, hash)
					await tofile(hash)
					with open('diagram.png', 'rb') as f:
						await interaction.channel.send(
							hash,
							file=discord.File(f)
						)

@bot.tree.command(name='tbt')
@app_commands.describe(
	hash = "the line of text the bot outputs",
	_x = "x coordinate",
	_y = "y coordinate",
	_xn = "when x is - (left)",
	_xp = "when x is + (right)",
	_yn = "when y is - (down)",
	_yp = "when y is + (up)",
	_1 = "1st quadrant",
	_2 = "2nd quadrant",
	_3 = "3rd quadrant",
	_4 = "4th quadrant",
	_t = "title of diagram",
	_pub = "True = publish, otherwise by default only you can see the bot reply",
	#add some more ...
)
async def tbt(interaction:discord.Interaction,
							hash:str=None,
								_x:str="",
								_y:str="",
								_xn:str="",
								_xp:str="",
								_yn:str="",
								_yp:str="",
								_1:str="",
								_2:str="",
								_3:str="",
								_4:str="",
								_t:str="",
							_pub:bool=False
						 	):

	hash = await tohash(hash)
	if hash == False:
		await interaction.response.send_message(
			"incorrect format ... or a bug?",
			ephemeral=True
		)

	else:
		hash = await amendhash(hash, [_x, _y, _xn, _xp, _yn, _yp, _1, _2, _3, _4, _t])
		await tofile(hash)
		# send to discord
		with open('diagram.png', 'rb') as f:
			await interaction.response.send_message(
				hash,
				file = discord.File(f),
				ephemeral = not _pub
			)
	

#### utility

options = [
	'_x','_y','_xn','_xp','_yn','_yp','_1','_2','_3','_4','_t',
	'x','y','xn','xp','yn','yp','1','2','3','4','t'
]



async def tohash(hash):
	if hash is None:
		return hash
	
	cuts = hash.split(", ")
	if len(cuts) == 1 and len(hash.split(" ")) == 1:
		if len(hash.split((HASH_DELIM))) == PARAM_NUM:
			return hash
		return False
		
	indexes = []
	values = []
	for cut in cuts:
		c = cut.split(" ")
		if len(c) == 1 or c[0] not in options:
			return False
		else:
			indexes.append(options.index(c[0]) % PARAM_NUM)
			values.append(" ".join(c[1:]))

	hash = ""
	for i in range(PARAM_NUM):
		if i in indexes:
			hash += values[indexes.index(i)]
		if i != PARAM_NUM - 1:
			hash += HASH_DELIM
	
	return hash


async def amendhash(hash=None, hash2=None):
	if hash2 == None:
		return hash
	if hash == None:
		if isinstance(hash2, list):
			return HASH_DELIM.join(hash2)
		else:
			return hash2
	if not isinstance(hash2, list):
		hash2 = hash2.split(HASH_DELIM)
		
	for i, keep in enumerate(hash.split(HASH_DELIM)):
		if hash2[i] == "":
			hash2[i] = keep
	return HASH_DELIM.join(hash2)



async def tofile(hash):
	[_x, _y, _xn, _xp, _yn, _yp, _1, _2, _3, _4, _t] = hash.split(HASH_DELIM)

	## draw
								
	width = 400
	height = 400
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
	
	
	# images
	img = Image.new('RGB', (width, height), color='white')
	
	# draws
	draw = ImageDraw.Draw(img)
	
	# fonts
	font = ImageFont.truetype('LDFComicSans.ttf', 16)
	font90 = ImageFont.TransposedFont(font, Image.ROTATE_90)

	# utilities
	def drawtextdefault(xy, text, font=font):
		draw.text(xy, text, font=font, fill="black")

	def drawlinedefualt(xy):
		draw.line(xy, fill='black')

	def getwidth(target):
		return font.getbbox(target)[2]

	def getheight(target):
		return font.getbbox(target)[3]


							
	# draw x lines, labels, limits
	drawlinedefualt((0, oy, width, oy))

	drawtextdefault((q1x-getwidth(_x)/2, oy), _x)

	drawtextdefault((0, oy-getheight(_xn)), _xn)
	drawtextdefault((width-getwidth(_xp), oy-getheight(_xp)), _xp)


	# draw y lines, labels, limits
	drawlinedefualt((ox, 0, ox, height))

	drawtextdefault((ox-getheight(_y), q1y-getwidth(_y)/2), _y, font90)

	drawtextdefault((ox, height-getheight(_yn)), _yn)
	drawtextdefault((ox, 0), _yp)
	

	# draw quadrant labels
	drawtextdefault((q1x-getwidth(_1)/2, q1y), _1)
	drawtextdefault((q2x-getwidth(_2)/2, q2y), _2)
	drawtextdefault((q3x-getwidth(_3)/2, q3y), _3)
	drawtextdefault((q4x-getwidth(_4)/2, q4y), _4)
	
	
	# draw _t
	drawtextdefault((0, 0), _t)
	
	# save image
	img.save('diagram.png')

bot.run(TOKEN)