import discord
import logging
import json
import resolve_host

from sys import exit
from pathlib import Path
from datetime import datetime
from discord.ext import commands

# TODO: Change debug to be a launch option instead of program variable
debug = True

"""
Parse JSON
"""

with open('config.json') as cfg:
    settings = json.load(cfg)
    cfg.close()

rgkey = settings['riot-api-key']

#Get region from config and set host
host = resolve_host.switch_platform(settings['region'].lower())
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
    await ctx.send(f"Done: {eval(args)}")

#If the debug flag is enabled log messages to console to ensure the bot is connected properly
@bot.event
async def on_message(message):
    if debug == True:
        print(f"{message.guild} - #{message.channel} - {message.author}({message.author.id}): {message.content}")
    await bot.process_commands(message)

bot.load_extension("verification")

bot.run(settings['bot-token'])