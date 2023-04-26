import discord
from discord import app_commands
from discord.ext import commands
import PIL
from PIL import Image, ImageDraw, ImageFont
import os

TOKEN = os.environ['your_bot_token_here']
EPHER = True
SAVED = None

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

@bot.tree.command(name='tbt')
@app_commands.describe(
	hash="bot outputs it as text",
	ephemeral="only you can see this"
	#add some more ...
)
async def tbt(interaction:discord.Interaction,
							hash:str=None,
								x_label:str="",
								y_label:str="",
								x_min_label:str="",
								x_max_label:str="",
								y_min_label:str="",
								y_max_label:str="",
								q1_label:str="",
								q2_label:str="",
								q3_label:str="",
								q4_label:str="",
								title:str="",
							ephemeral:bool=True
						 	):

	params = [
		x_label,
		y_label,
		x_min_label,
		x_max_label,
		y_min_label,
		y_max_label,
		q1_label,
		q2_label,
		q3_label,
		q4_label,
		title
	]

	#might want to amend by replying to bot
	if hash != None:
		for i, keep in enumerate(hash.split(".:.")[1:-1]):
			if params[i] == "":
				params[i] = keep
		
		#might want to record amend action
		#might want hash to be polymorphic as prompt
		pass
	else:
		pass

	#should add escape
	tbt = ".:." + (".:.").join(params) + ".:."
								
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

	drawtextdefault((q1x-getwidth(x_label)/2, oy), x_label)

	drawtextdefault((0, oy-getheight(x_min_label)), x_min_label)
	drawtextdefault((width-getwidth(x_max_label), oy-getheight(x_max_label)), x_max_label)


	# draw y lines, labels, limits
	drawlinedefualt((ox, 0, ox, height))

	drawtextdefault((ox-getheight(y_label), q1y-getwidth(y_label)/2), y_label, font90)

	drawtextdefault((ox, height-getheight(y_min_label)), y_min_label)
	drawtextdefault((ox, 0), y_max_label)
	

	# draw quadrant labels
	drawtextdefault((q1x-getwidth(q1_label)/2, q1y), q1_label)
	drawtextdefault((q2x-getwidth(q2_label)/2, q2y), q2_label)
	drawtextdefault((q3x-getwidth(q3_label)/2, q3y), q3_label)
	drawtextdefault((q4x-getwidth(q4_label)/2, q4y), q4_label)
	
	
	# draw title
	drawtextdefault((0, 0), title)
	
	# save image
	img.save('diagram.png')
	
	# send to discord
	with open('diagram.png', 'rb') as f:
		await interaction.response.send_message(
			tbt,
			file=discord.File(f),
			ephemeral=ephemeral
		)

bot.run(TOKEN)