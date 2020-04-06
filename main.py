import discord
import logging
import json
import sqlite3
import requests

import checks
import resolve_host

from sys import exit
from pathlib import Path
from datetime import datetime
from discord.ext import commands

# TODO: Change debug to be a launch option instead of program variable
debug = True

def switch_platform(arg):
    switch = {
        'br': 'br1',
        'eun': 'eun1',
        'euw': 'euw1',
        'jp': 'jp1',
        'kr': 'kr',
        'lan': 'la1',
        'las': 'la2',
        'na': 'na1',
        'oce': 'oc1',
        'tr': 'tr1',
        'ru': 'ru'
    }

    host = switch.get(arg, '-1')

    if host == '-1':
        return '-1'
    else:
        return 'https://' + host + '.api.riotgames.com/lol/' 


"""
Parse JSON
"""

with open('config.json') as cfg:
    settings = json.load(cfg)
    cfg.close()

rgkey = settings['riot-api-key']

#Get region from config and set host
host = switch_platform(settings['region'].lower())
if host == '-1':
    print("ERROR: Region in config is invald, must be one of the folowing: ['br', 'eun', 'euw', 'jp', 'kr', 'lan', 'las', 'na', 'oce', 'tr', 'ru']")
    exit(1)

"""
Set up logging
"""

Path('logs').mkdir(parents=True, exist_ok=True)
logfile = 'logs/' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.log'

logger = logging.getLogger('discord')

if debug == True:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

loghandler = logging.FileHandler(filename=logfile, encoding='utf-8', mode='w')
loghandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(loghandler)

"""
Start Bot
"""

bot = commands.Bot(command_prefix=settings['prefix'])

#TODO: Put champ quotes in a file and random pull
@bot.event
async def on_ready():
    print("Ready to set the world on fire? hehehe... -Brand")
    await bot.change_presence(activity=discord.Game(name="with the enemy support"))

#A test command to make sure that the bot is hooking into the Discord API properly
@bot.command()
async def ping(ctx):
    await ctx.send(f":ping_pong: Pong! `{round(bot.latency*1000, 2)} ms`")

#A test command to make sure the bot is handling arguments properly in the current context
@bot.command()
async def echo(ctx, *, args):
    await ctx.send(args)

#A COMMAND ONLY FOR TESTING HOTLOADING OF COGS/EXTENSIONS TO BE REMOVED IN RELEASES
@bot.command(name="eval")
@commands.is_owner()
async def _eval(ctx, *, args):
    logger.info(f"Ran the following eval code, unexpected behavior beyond this point: {args}")
    await ctx.send(f"Done: {eval(args)}")

#If the debug flag is enabled log messages to console to ensure the bot is connected properly
@bot.event
async def on_message(message):
    if debug == True:
        print(f"{message.guild} - #{message.channel} - {message.author}({message.author.id}): {message.content}")
    await bot.process_commands(message)

"""
Verification
"""

@bot.command()
@commands.check(checks.is_unverified)
@commands.guild_only()
async def register(ctx, *, args):
    logger.info(f"{ctx.author}({ctx.author.id}) invoked 'register'")

    member = ctx.author.id

    #Check to see if the summoner that was passed in is real on the server in config
    parsed_summoner = requests.utils.quote(args)
    query = host + 'summoner/v4/summoners/by-name/' + parsed_summoner
    payload = {'api_key': rgkey}
    response = requests.get(query, params=payload)
    summoner = response.json()

    if response.status_code == 404:
        await ctx.send(f"<@{member}>, no information was found for the summoner \"{args}\" on the {settings['region'].upper()} server.")
        return
    elif response.status_code != 200:
        try:
            await ctx.send(f"<@{member}> ERROR {summoner['status']['status_code']}: {summoner['status']['message']}")
        except:
            await ctx.send(f"<@{member}> ERROR {response.status_code}, no other information is available.")
        return

    #Add the user to the DB in the unverified table
    info = (str(member), summoner['name'])

    conn = sqlite3.connect('server.db')
    c = conn.cursor()
    c.execute("INSERT INTO unverified VALUES (?,?)", info)
    conn.commit()
    logger.info(f"Wrote {str(info)} to table unverified")
    conn.close()

    #Create the DM to send to the user
    f = discord.File("verification.gif", filename="verification.gif")
    message = "Thank you for registering! Currently your summoner name is unverified, so you will be unable to queue until you verify it.\n"
    message = message + "To do so, enter the verification code `" + str(member) + "` in the third-party verification tab in your LoL account. "
    message += "To find this entry field, click the gear then select \"Verification\" under the \"About\" tab as show in the attached gif.\n"
    message += "Once you've entered the verification code, reply to me with `" + settings['prefix'] + "done` to complete the process."

    #Send the DM and reply to the user in the guild
    await ctx.author.send(message, file=f)
    await ctx.send(f"<@{member}>, check your DMs for verification information.")

@register.error
async def register_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        pass
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(f"<@{ctx.author.id}>, you cannot register, you may be already registered or are currently in the verification process.")
    elif isinstance(error, commands.CommandInvokeError):
        member = (str(ctx.author.id),)
        conn = sqlite3.connect('server.db')
        c = conn.cursor()
        c.execute('DELETE FROM unverified WHERE discordId=?', member)
        conn.commit()
        logger.info(f"CommandInvokeError caused me to delete entry {ctx.author.id} from table unverified")
        conn.close()
        
        await ctx.send(f"<@{ctx.author.id}>, something went wrong. Do you have \"allow direct messages from server members\" disabled?")
        logger.error(f"{error}")
    else:
        logger.error(f"{ctx.author}({ctx.author.id}) encountered the following error: {error}")

@bot.command()
@commands.check(checks.pending_verification)
@commands.dm_only()
async def done(ctx):
    logger.info(f"{ctx.author}({ctx.author.id}) invoked 'done'")

    member = ctx.author.id

@done.error
async def done_error(ctx, error):
    if isinstance(error, commands.PrivateMessageOnly):
        pass
    elif isinstance(error, commands.CheckFailure):
        await ctx.send(f"You are not in the verification process.")
    elif isinstance(error, commands.CommandInvokeError):
        #TODO: Add stuff here where user is put back into unverified and removed from verified
        logger.error(f"{error}")
    else:
        logger.error(f"{ctx.author}({ctx.author.id}) encountered the following error: {error}")

bot.run(settings['bot-token'])