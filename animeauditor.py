import string
import random
import cv2
import sys
import os
import os.path
import urllib.request
import discord
from discord.ext import commands

TOKEN = 'YourTokenHere!'

client = commands.Bot(command_prefix = 'aa?')
client.remove_command('help')

dev_key = ''

# Function run on ready
@client.event
async def on_ready():

	print('> Anime Auditor reports all systems green.')
	regenerate_key()

'''
Ping command. This command prints 'Pong!' when called.
'''
@client.command()
async def ping():
	await client.say('Pong!')

'''
Help command. This command prints an embed listing all the commands.

param ctx - call context.
'''
@client.command(pass_context = True)
async def help(ctx):

	embed = discord.Embed(

		title='Displaying Manual :notepad_spiral:',
		description='The following are all of **Anime Auditor**\'s commands.',
		color=0x7a7a7a
	)

	embed.add_field(name='Command', value='aa?help\naa?credits\naa?ping\naa?auditme\naa?audit [user]\naa?auditserver')
	embed.add_field(name='Description', value='Display user manual.\nDisplay dependency authors.\nPong!\nAnime audit your own avatar.\nAnime audit a user\'s avatar.\nAnime audit the entire server.')

	await client.send_message(ctx.message.channel, embed=embed)

'''
Credits command. This prints an embed listing the credits.

param ctx - call context.
'''
@client.command(pass_context = True)
async def credits(ctx):

	embed = discord.Embed(

		title='Displaying Credits :notepad_spiral:',
		description='The following people and organizations helped make **Anime Auditor**.',

		color=0x7a7a7a
	)

	embed.add_field(name='Author', value='CptNubz\nSurprisinglyFun\nNagadomi\nOpenCV')
	embed.add_field(name='Contribution', value='Discord.py implementation.\nMoral Support.\nFace detector for anime faces.\nOpen source computer vision library.')

	await client.send_message(ctx.message.channel, embed=embed)

'''
Blacklist command. This adds a user name to the blacklist. Users on the blacklist will always be reported as anime positive.

param ctx - call context.
param name - the discord name of the user to blacklist.
param key - authorization key.
'''
@client.command(pass_context = True)
async def blacklist(ctx, name='JjVeZnTHQyEH7', key='JjVeZnTHQyEH7'):

	global dev_key

	# Check if the caller gave a target by checking if values are default. If so, abort.

	if (name is 'JjVeZnTHQyEH7') or (key is 'JjVeZnTHQyEH7'):

		err_embed = make_embed_err('A name or authorization key was not passed to command.')
		return await client.send_message(ctx.message.channel, embed=err_embed)

	# Check if the caller gave a valid dev. If not, abort.

	if(dev_key == key):

		regenerate_key()
		f = open('blacklist.txt', 'a')
		f.write(name+'\n')
		regenerate_key()

		embed = discord.Embed(

			title='Blacklist updated. :flag_black:',
			description='The name **' + name + '** has been added to the blacklist.',
			color=0x000000
		)

		await client.send_message(ctx.message.channel, embed=embed) # Send message.

	else:

		err_embed = make_embed_err('Incorrect authorization key.')
		return await client.send_message(ctx.message.channel, embed=err_embed) # Send error.

'''
Audit server command. This command audits every user in the server for anime.

param ctx - call context.
'''
@client.command(pass_context = True)
async def auditserver(ctx, arg = 'F'):

	print('> User ' + ctx.message.author.name + ' on ' + ctx.message.server.name + ' ran command AUDITSERVER.');

	# Get all members.
	member_arr = ctx.message.server.members
	member_count = 0
	anime_count = 0

	# Generate the local file paths.
	local_in = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_in.png')
	local_out = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_out.png')

	if arg.lower() is 'role':

		# Check if role exists.
		checkRole = None
		checkRole = discord.utils.get(ctx.message.author.server.roles, name='Weaboo')

		if checkRole is None:
			await client.create_role(ctx.message.author.server, name='Weaboo', colour=discord.Colour(0x800080))

	# Loop through all members in server.
	for m in member_arr:

		print('> DEBUG: checking ' + m.name)

		# Iterate member count.
		member_count += 1

		# Download m's avatar.
		abort = download_avatar(ctx, m)
		
		# The avatar was default. Abort.
		if abort:
			continue

		# Test avatar.
		is_anime = detect(ctx, local_in)

		is_blacklist = detectblacklist(ctx, m)
		if (is_blacklist == True) and (is_anime == False):
			is_anime = True

		# If anime detected, send file.
		if is_anime:
			anime_count += 1

			# If arg is role, add user to role.
			if arg is 'role':
				role = discord.utils.get(m.server.roles, name='Weaboo')
				await client.add_roles(m, role)

			await client.send_file(ctx.message.channel, local_out, content='Member **' + m.name + '** has tested anime positive. :white_check_mark:', filename=local_out) # Send image.

	# Don't include the bot.
	member_count -= 1 

	# Generate message for embed.
	msg = '**%s** users have tested anime **positive**.\n**%s** users have tested anime **negative**.\n**% 6.2f** percent of users on this server have anime avatars.' % (anime_count, (member_count - anime_count), 100*(anime_count/member_count))
	
	# Generate embed.
	embed = discord.Embed(

		title='Server Anime Audit Complete :mag:',
		description='Every user on this server has had their avatar analysed by computer vision software.',
		color=0xf9900e
	)

	embed.add_field(name='Server Anime Status', value=msg)
	embed.set_footer(text='Generated using OpenCV2 and Nagadomi\'s face detector.')

	await client.send_message(ctx.message.channel, embed=embed) # Send Message.

'''
Audit user command. This command audits a user for anime.

param ctx - call context.
param target_name - the user name of target member.
'''
@client.command(pass_context = True)
async def audit(ctx, target_name = 'JjVeZnTHQyEH7'):

	print('> User ' + ctx.message.author.name + ' on ' + ctx.message.server.name + ' ran command AUDIT.');

	# Check if the caller gave a target. If not, abort.
	if target_name is 'JjVeZnTHQyEH7':
		err_embed = make_embed_err('A name was not passed to command.')
		return await client.send_message(ctx.message.channel, embed=err_embed)

	# Search all members for user name passed to command.
	member_arr = ctx.message.server.members
	target_member = None
	for member in member_arr:
		if target_name.lower() == member.name.lower():
			target_member = member
			break

	# Check if user found. If not, abort.
	if target_member is None:
		err_embed = make_embed_err('A member with that name was not found.')
		return await client.send_message(ctx.message.channel, embed=err_embed)

	# Download the targer member's avatar.
	abort = download_avatar(ctx, target_member)

	# The avatar was default. Abort.
	if abort:
		err_embed = make_embed_err('A user with a default avatar cannot be anime audited.')
		return await client.send_message(ctx.message.channel, embed=err_embed) # Send error.

	# Generate the local file paths.
	local_in = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_in.png');
	local_out = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_out.png')

	# Test avatar.
	is_anime = detect(ctx, local_in)

	# Test against blacklist.
	is_blacklist = detectblacklist(ctx, target_member)
	if (is_blacklist == True) and (is_anime == False):
		is_anime = True

	# Generate embed message.
	if is_anime:
		embed = discord.Embed(
			title='Anime Audit Complete :mag:',
			description='The user **%s** has had their avatar analysed by computer vision software.' % (target_member.name),
			color=0x6be121
		)
		embed.add_field(name='Anime Status', value='Anime **is** Detected :white_check_mark:')
	else:
		embed = discord.Embed(
			title='Anime Audit Complete :mag:',
			description='The user **%s** has had their avatar analysed by computer vision software.' % (target_member.name),
			color=0xe01f1f
		)
		embed.add_field(name='Anime Status', value='Anime **not** Detected :x:')

	# Set footer credits. Common to both cases.
	embed.set_footer(text='Generated using OpenCV2 and Nagadomi\'s face detector.')

	# Send data to discord.
	await client.send_file(ctx.message.channel, local_out, content='', filename=local_out) # Send image.
	await client.send_message(ctx.message.channel, embed=embed) # Send Message.

'''
Audit me command. This command audits the caller for anime.

param ctx - call context.
'''
@client.command(pass_context = True)
async def auditme(ctx):
	
	print('> User ' + ctx.message.author.name + ' on ' + ctx.message.server.name + ' ran command AUDITME.');

	# Download the author's avatar.
	abort = download_avatar(ctx, ctx.message.author)

	# The avatar was default. Abort.
	if abort:
		err_embed = make_embed_err('A user with a default avatar cannot be anime audited.')
		return await client.send_message(ctx.message.channel, embed=err_embed) # Send error.

	# Generate the local file paths.
	local_in = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_in.png');
	local_out = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_out.png')

	# Test avatar.
	is_anime = detect(ctx, local_in)

	# Test against blacklist.
	is_blacklist = detectblacklist(ctx, ctx.message.author)
	if (is_blacklist == True) and (is_anime == False):
		is_anime = True

	# Generate embed message.
	if is_anime:
		embed = discord.Embed(
			title='Anime Audit Complete :mag:',
			description='The user **%s** has had their avatar analysed by computer vision software.' % (ctx.message.author.name),
			color=0x6be121
		)
		embed.add_field(name='Anime Status', value='Anime **is** Detected :white_check_mark:')
	else:
		embed = discord.Embed(
			title='Anime Audit Complete :mag:',
			description='The user **%s** has had their avatar analysed by computer vision software.' % (ctx.message.author.name),
			color=0xe01f1f
		)
		embed.add_field(name='Anime Status', value='Anime **not** Detected :x:')
	
	# Set footer credits. Common to both cases.
	embed.set_footer(text='Generated using OpenCV2 and Nagadomi\'s face detector.')

	# Send data to discord.
	await client.send_file(ctx.message.channel, local_out, content='', filename=local_out)
	await client.send_message(ctx.message.channel, embed=embed)

'''
Regenerate the dev key.
'''
def regenerate_key():

	global dev_key
	dev_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
	print('> Up to date dev key: ' + dev_key)

'''
Download avatar function. This function takes a context and downloads the user's avatar from it.

param ctx - call context.
param member - the member whose avatar to download.
return bool - TRUE if avatar is default. FALSE if not.
'''
def download_avatar(ctx, member):

	# Check for default avatar.
	if member.avatar is None:
		return True

	# Create endpoint.
	direct_pfp = 'https://cdn.discordapp.com/avatars/' + member.id + '/' + member.avatar + '.png?size=128' 
	
	# Download the image for proccessing.
	opener=urllib.request.build_opener()

	# Change the user agent. This is necessary because the URL will 403 if loaded from a web scraper.
	opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')] # Change user agent.
	urllib.request.install_opener(opener)
	url=direct_pfp

	# If no path, create it.
	if not os.path.exists(os.path.join('servers', ctx.message.server.id)):
	    os.makedirs(os.path.join('servers', ctx.message.server.id))

	# Generate the local file path.
	local = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_in.png');

	# Download avatar picture as in.png.
	urllib.request.urlretrieve( url,local) 

	return False

'''
OpenCV2 detect function. This function checks if an image has anime in it, then returns a TRUE or FALSE.

param ctx - call context.
param member - the member whose avatar to download.
param filename - image to be audited.
param cascade_file - face detection file.
return bool - TRUE if face found. FALSE if not.
'''
def detect(ctx, filename, cascade_file = 'lbpcascade_animeface.xml'):

	if not os.path.isfile(cascade_file):
		raise RuntimeError('%s: not found' % cascade_file)

	cascade = cv2.CascadeClassifier(cascade_file)
	image = cv2.imread(filename, cv2.IMREAD_COLOR)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.equalizeHist(gray)
	
	faces = cascade.detectMultiScale(gray,
									 # Detector options. Yeah, I've got no clue.
									 scaleFactor = 1.1,
									 minNeighbors = 1,
									 minSize = (24, 24))
	for (x, y, w, h) in faces:
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

	cv2.waitKey(0)

	# If no path, create it.
	if not os.path.exists(os.path.join('servers', ctx.message.server.id)):
	    os.makedirs(os.path.join('servers', ctx.message.server.id))

	# Generate the local file path.
	local = os.path.join('servers', ctx.message.server.id, ctx.message.author.id + '_out.png');

	# Write to local file path.
	cv2.imwrite(local, image)

	if faces == ():
		return False
	else:
		return True

'''
Blacklist detect function. This function checks if a member is blacklisted, then returns a TRUE or FALSE.

param ctx - call context.
param member - the member who to check for.
return bool - TRUE if face found. FALSE if not.
'''
def detectblacklist(ctx, member):

	f = open('blacklist.txt', 'r')
	found = False;
	for x in f:
		x = x.rstrip('\n\r')
		if member.name == x:
			found = True

	return found

'''
Create error embed. This function generates an error message embed.

param msg - the text to be in the error embed.
'''
def make_embed_err(msg):

	embed = discord.Embed(
		title='An Error as occured. :rotating_light:',
		description='**Error Description**: ' + msg,
		color=0xe01f1f
	)

	return embed

client.run(TOKEN)