#! /usr/bin/env python3
"""
	This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord
import random
from discord.ext import commands
from datetime import datetime
# Logging
import logging

info_logger = logging.getLogger('discord')
info_logger.setLevel(logging.INFO)
debug_logger = logging.getLogger('discord')
debug_logger.setLevel(logging.DEBUG)
info_handler = logging.FileHandler(filename='logs/info.cnlog', encoding='utf-8', mode='w')
debug_handler = logging.FileHandler(filename='logs/debug.cnlog', encoding='utf-8', mode='w')
info_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
info_logger.addHandler(info_handler)
debug_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
debug_logger.addHandler(debug_handler)

# Bot setup, and global variables that make things easier for me
bot = commands.Bot(command_prefix='$')
client = discord.Client()
RIGGED = False
DB = "DB/database.cndb"
DBTMP = "DB/tmp.cncrypt"

# OC dont steal
TOKEN = ""
with open("enc/token.cncrypt", "r+") as tfile:
	TOKEN = tfile.readline()

@bot.event
async def on_ready():
	now = datetime.now()
	date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
	print("Thank you for using this incredibly strange bot!")
	print("Setup complete -- Ready to cheat on dicerolls\t\t\t\t\t\t{}".format(date_time))
	print("--------------------------------------------------------------------------------------------------------------")

bot.remove_command('help')
# An help
@bot.command()
async def help(ctx):
	"""
	help: 	
			displays a help message
	Requires:
			Nothing
	"""
	print("({}) {} used $help".format(ctx.message.author.id, ctx.message.author.name))
	msg = discord.Embed(title="CN Diceroller", description="Commands:", color=0xff00ff)
	msg.add_field(name="$help", value="Displays this message", inline=False)
	msg.add_field(name="$roll <sides>", value="Rolls a variable-sided die and prints the result", inline=False)
	msg.add_field(name="$rigg", value="Nice try", inline=False)
	msg.add_field(name="$rigged", value="How dare you!", inline=False)
	msg.add_field(name="$dg <bet>", value="Dicegame, betting ¤<bet> against a 100-sided roll, over 55 is a win", inline=False)
	msg.add_field(name="$register", value="Registers you in the DB, requirement for gambling", inline=False)
	msg.add_field(name="$register_other <@user>", value="(ADMIN) Registers someone else, in case of error", inline=False)
	msg.add_field(name="$debug", value="(ADMIN) DB debug command", inline=False)
	msg.add_field(name="$update <@user> <amount>", value="(ADMIN) Give a user the provided amount", inline=False)
	await ctx.send(embed=msg)
	

# Roll a dice with a variable amount of sides
@bot.command()
async def roll(ctx, max: int):
	"""
	Roll: 	
			performs a riggable roll, printing the result in the chat used, utilizing the sides provided.
	Requires:
			Nothing
	"""
	global RIGGED
	author = ctx.message.author
	print("({}) {} used $roll with {} sides".format(author.id, author.name, max))
	if max <= 1:
		# Someone will definitely attempt to roll a "0 sided die" and thats dumb
		await ctx.send("```Are you braindead? Do you not know how dice work?```")
		return
	roll = random.randint(1, max)
	if RIGGED:
		# If you wanna rigg a throw, make sure it always gets the max
		await ctx.send('```Rolled a {}```'.format(max))
		RIGGED = False
		print("Rig successfull, returning to standard, boring \"FAIR\" mode.")
	else:
		await ctx.send("```Rolled a {}```".format(roll))

# Rigg the next roll
@bot.command()
async def rigg(ctx):
	"""
	Rigg: 	
			riggs the next roll of any dice, regardless of source.
	Requires:
			Administrator permission, to stop users from cheating (but not admins ;))
	"""
	global RIGGED
	author = ctx.message.author
	is_admin: bool = author.top_role.permissions.administrator
	print("({}) {} used $rigg | Is admin: {}".format(author.id, author.name, is_admin))
	# Dont want the plebians to do this
	if is_admin:
		RIGGED = True
		print("It'll be our little secret ;)")
		# Hide the evidence
		await ctx.message.delete()
	else:
		# monkaS
		print("{} is onto us, keep an eye out :eyes:".format(ctx.message.author.name))
		await ctx.send("```I'm deeply offended that you'd assume I have such functionality```")

# If someone were to be so incredulous as to accuse the bot
@bot.command()
async def rigged(ctx):
	"""
	Rigged: 	
			accuses the bot of being rigged, which is incredibly disrespectful *cough*
	Requires:
			Nothing
	"""
	author = ctx.message.author
	print("({}) {} used $rigged".format(author.id, author.name))
	await ctx.send("```How DARE you accuse me of rigging something as holy as a dice throw you degenerate manatee!```")

# Dice game, most of the code is DB stuff
@bot.command()
async def dg(ctx, bet):
	"""
	dg: 	
			rolls a 100-sided die with a provided bet, and pays out double if above 55.
	Requires:
			User must be registered and have a sufficient balance to play the game
	"""
	global RIGGED
	global DB
	global DBTMP
	author = ctx.message.author
	print("({}) {} used $dg for ¤{}".format(author.id, author.name, bet))
	# get the current userid (db stuff)
	if RIGGED:
		# make sure we win if its rigged
		roll = random.randint(55, 100)
		# debug info
		print("{} rolled a {} in DG, Rigged: {}".format(ctx.message.author.name, roll, RIGGED))
		RIGGED = False
	else:
		# fair and boring roll
		roll = random.randint(1, 100)
		# debug info
		print("{} rolled a {} in DG, Rigged: {}".format(ctx.message.author.name, roll, RIGGED))
	line = "0000000000"
	# HERE WE GOOO
	with open(DB, "r+") as db:
		while line != "":
			try: # Use exceptions to find the EOF
				line = db.readline()
				if str(author.id) in line: # If we found the user
					split: list = line.split("/") # Get the balance and id seperately
					bal: str = split[1] 
					balint = int(bal)
					print("Old balance: {}".format(balint))
					if balint < int(bet): # cant bet more than you have
						await ctx.send("```Illegal bet -  You dont have that much!```")
						return
					if roll <= 55:
						balint -= int(bet) # lol loser
						await ctx.send("```I'm sorry {}, you lose with a roll of {}, losing ¤{}```".format(ctx.message.author.name, roll, bet))
					else:
						balint += int(bet) # gg no re
						await ctx.send("```Congrats {}, you win with a roll of {}, earning ¤{}```".format(ctx.message.author.name, roll, bet))
					print("New balance: {}".format(balint))
					bal = str(balint)
					split[1] = bal
					newline = split[0] + "/" + split[1] # make the new db entry
					tmpdata = "0000000"
					with open(DBTMP, "w") as clear: # clear the tmp file, just in case
						clear.write("")
					with open(DBTMP, "r+") as tmp:  # transfer all db info to temporary storage
						with open(DB, "r+") as db:
							while tmpdata != "":
								dbline = db.readline()
								tmpdata = dbline
								if dbline == line:			# write the new line instead of the old one
									tmp.write(newline+"\n")
								else:
									tmp.write(dbline+"\n")
					tmpdata = "0000000"
					with open(DB, "w") as clear:		# clear the db
						clear.write("")
					with open(DB, "r+") as db:			# rewrite the db for future use
						with open(DBTMP, "r+") as tmp:
							while tmpdata != "":
								tmpdata = tmp.readline()
								if(tmpdata != "\n"): db.write(tmpdata)
					with open(DBTMP, "w") as clear:	# clear tmp to have it ready for the next pass
						clear.write("")
					return
			except StopIteration:
				print("End of file hit in DB search")	# EOF, tell them off for big dumbdumb
				await ctx.send("```Trying to gamble without money is kinda dumb```")
				return

# Register a user to the bot DB
@bot.command()
async def register(ctx):
	"""
	Register: 	
			registers the user who uses the command in the db and grants them a free ¤1000.
	Requires:
			Must not be registered already
	"""
	global DB
	author = ctx.message.author
	print("({}) {} used $register".format(author.id, author.name))
	line: str = "0000000000000"
	with open(DB, "r+") as db: # ah shit, here we go again
		while line != "":
			try:
				line = db.readline()		# check users
				if str(author.id) in line:
					split: list = line.split("/")
					print("({}) {} is already registered".format(author.id, author.name))
					bal: str = split[1]		# registering someone twice would be stupid
					await ctx.send("```You're already registered, {}! You have ¤{} currently```".format(author.name, bal))
					return
			except StopIteration:			# register them if they're not in the DB
				print("End of file hit in DB search")
		db.write(str(author.id) + "/1000\n")
	await ctx.send("**User {} has been registered!**".format(author.mention))

# Register another user to the bot DB
@bot.command()
async def register_other(ctx, user: discord.User):
	"""
	Register other: 	
			registers another user in the db, mainly in case of.
	Requires:
			Administrator permission, no need for others to tag people constantly for no reason
	"""
	global DB
	author = ctx.message.author
	is_admin: bool = author.top_role.permissions.administrator
	print("({}) {} used $register_other on ({}) {} | Is admin: {}".format(author.id, author.name, user.id, user.name, is_admin))
	if is_admin:
		line: str = "0000000000000"
		with open(DB, "r+") as db: # ah shit, here we go again
			while line != "":
				try:
					line = db.readline()		# check users
					if str(user.id) in line:
						split: list = line.split("/")
						print("({}) {} is already registered".format(user.id, user.name))
						bal: str = split[1]		# registering someone twice would be stupid
						await ctx.send("```{} is already registered! They have ¤{} currently```".format(user.name, bal))
						return
				except StopIteration:			# register them if they're not in the DB
					print("End of file hit in DB search")
			db.write(str(user.id) + "/1000\n")
		await ctx.send("**User {} has been registered!**".format(user.mention))
	else:
		await ctx.send("```You dont look like an admin to me```")

# Show a user their balance
@bot.command()
async def bal(ctx):
	"""
	Bal: 	
			responds with the users balance.
	Requires:
			user must be registered
	"""
	global DB
	author = ctx.message.author
	print("({}) {} used $bal".format(author.id, author.name))
	line: str = "0000000000000"
	with open(DB, "r+") as db: # getting really tired of file i/o
		while line != "":
			try:
				line = db.readline()
				if str(author.id) in line:
					split: list = line.split("/") # if we find them, respond with their balance and cease
					bal: str = split[1]
					print("({}) {} has ¤{}".format(author.id, author.name, bal))
					await ctx.send("```{} has ¤{}```".format(author.name, bal))
					return
			except StopIteration:
				print("End of file hit in DB search") # let them know if they're stupid
				await ctx.send("```You have to be registered to have money, silly```")

# Get some debug info in the console
@bot.command()
async def debug(ctx):
	"""
	Debug: 	
			prints the current db state and global information to the console, to aid in troubleshooting
			db issues.
	Requires:
			Administrator permission, to stop users from spamming the console with debug info
	"""
	global DB
	author = ctx.message.author
	is_admin: bool = author.top_role.permissions.administrator
	print("({}) {} used $debug | Is admin: {}".format(author.id, author.name, is_admin))
	# I really dont want people to spam debug info
	if is_admin:
		registered_users: int = 0
		total_balance: int = 0
		line: str = "0000000000000"
		with open(DB, "r+") as db: # getting really tired of file i/o
			while line != "":
				try:
					line = db.readline() # calculate totals and print individual info
					split: list = line.split("/")
					if len(split) >1:	 # ghost users are a thing
						bal: str = split[1]
						registered_users += 1
						total_balance += int(bal)
						print("User: {} - Balance: ¤{}".format(split[0], bal))
				except StopIteration:
					print("End of file hit in DB search") # in case the while fails
					break
		print("Total users: {}\t\tTotal balance: {}".format(registered_users, total_balance))
	else:
		await ctx.send("```Nice try, pleb```")

# Change someones balance
@bot.command()
async def update(ctx, user: discord.User, amount: int):
	"""
	Update: 	
			gives the specified user <amount> extra ¤.
	Requires:
			Administrator permission, for what i hope is an obvious reason. User must also be registered
	"""
	global RIGGED
	global DB
	global DBTMP
	author = ctx.message.author
	is_admin: bool = author.top_role.permissions.administrator
	print("({}) {} used $update on ({}) {} for ¤{} | Is admin: {}".format(author.id, author.name, user.id, user.name, amount, is_admin))
	# I really dont want normal people to do this
	if is_admin:
		line = "0000000000"
		# HERE WE GOOO
		with open(DB, "r+") as db:
			while line != "":
				try: # Use exceptions to find the EOF
					line = db.readline()
					if str(user.id) in line: # If we found the user
						print("User found for update ({})".format(user.id))
						split: list = line.split("/") # Get the balance and id seperately
						bal: str = split[1] 
						balint = int(bal)
						print("Old balance: {}".format(balint))
						balint += amount
						await ctx.send("```Balance of {} updated, You now have ¤{}```".format(user.name, balint))
						print("New balance: {}".format(balint))
						bal = str(balint)
						newline = str(user.id) + "/" + bal # make the new db entry
						tmpdata = "0000000"
						with open(DBTMP, "w") as clear: # clear the tmp file, just in case
							clear.write("")
						with open(DBTMP, "r+") as tmp:  # transfer all db info to temporary storage
							with open(DB, "r+") as db:
								while tmpdata != "":
									dbline = db.readline()
									tmpdata = dbline
									if dbline == line:			# write the new line instead of the old one
										tmp.write(newline+"\n")
									else:
										tmp.write(dbline+"\n")
						tmpdata = "0000000"
						with open(DB, "w") as clear:		# clear the db
							clear.write("")
						with open(DB, "r+") as db:			# rewrite the db for future use
							with open(DBTMP, "r+") as tmp:
								while tmpdata != "":
									tmpdata = tmp.readline()
									if(tmpdata != "\n"): db.write(tmpdata)
						with open(DBTMP, "w") as clear:	# clear tmp to have it ready for the next pass
							clear.write("")
						return
				except StopIteration:
					print("End of file hit in DB search")	# EOF, tell them off for big dumbdumb
					await ctx.send("```They need an account to be eligible for a balance update```")
					return
	else:
		await ctx.send("```Thats a no from me dawg```")

@bot.command()
async def raffle(ctx, prize: int):
	global DB
	global RIGGED
	author = ctx.message.author
	is_admin: bool = author.top_role.permissions.administrator
	winner_id = ""
	print("({}) {} used $raffle for ¤{} | Is admin: {}".format(author.id, author.name, prize, is_admin))
	if is_admin:
		user_ids: list = []
		line: str = "000000000"
		if RIGGED:
			winner_id = str(author.id)
			print("Rigged for : {}".format(winner_id))
			RIGGED = False
		else:
			with open(DB, "r+") as db:
				while line != "":
					try:
						line = db.readline()
						split = line.split("/")
						current_id = split[0]
						if current_id != "": user_ids.append(current_id)
					except StopIteration:
						print("Hit end of db search")
			roll = random.randint(0, len(user_ids))
			winner_id = user_ids[roll]
		line = "0000000"
		with open(DB, "r+") as db:
			while line != "":
				try: # Use exceptions to find the EOF
					line = db.readline()
					if winner_id in line: # If we found the user
						split: list = line.split("/") # Get the balance and id seperately
						bal: str = split[1] 
						balint = int(bal)
						print("Winner is {}".format(winner_id))
						print("Old balance: {}".format(balint))
						balint += prize
						await ctx.send("**Congrats <@{}>! You just won ¤{}**".format(winner_id, prize))
						print("New balance: {}".format(balint))
						bal = str(balint)
						newline = winner_id + "/" + bal # make the new db entry
						tmpdata = "0000000"
						with open(DBTMP, "w") as clear: # clear the tmp file, just in case
							clear.write("")
						with open(DBTMP, "r+") as tmp:  # transfer all db info to temporary storage
							with open(DB, "r+") as db:
								while tmpdata != "":
									dbline = db.readline()
									tmpdata = dbline
									if dbline == line:			# write the new line instead of the old one
										tmp.write(newline+"\n")
									else:
										tmp.write(dbline+"\n")
						tmpdata = "0000000"
						with open(DB, "w") as clear:		# clear the db
							clear.write("")
						with open(DB, "r+") as db:			# rewrite the db for future use
							with open(DBTMP, "r+") as tmp:
								while tmpdata != "":
									tmpdata = tmp.readline()
									if(tmpdata != "\n"): db.write(tmpdata)
						with open(DBTMP, "w") as clear:	# clear tmp to have it ready for the next pass
							clear.write("")
						return
				except StopIteration:
					print("End of file hit in DB search")	# EOF, tell them off for big dumbdumb
					await ctx.send("```They need an account to be eligible for a raffle win (i.e. something went wrong)```")
					return


bot.run(TOKEN)
