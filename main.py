import discord
import logging
import json
import requests
import sqlite3

from sys import exit
from pathlib import Path
from datetime import datetime
from discord.ext import commands

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
    return switch.get(arg, '-1')

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
host = switch_platform(settings['region'].lower())
if host == '-1':
    print("ERROR: Region in config is invald, must be one of the folowing: ['br', 'eun', 'euw', 'jp', 'kr', 'lan', 'las', 'na', 'oce', 'tr', 'ru']")
    exit(1)
host = 'https://' + host + '.api.riotgames.com/lol/'

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

#A test command to make sure that the bot is hooking into the Discord API properly
@bot.command()
async def ping(ctx):
    await ctx.send(f":ping_pong: Pong! `{round(bot.latency*1000, 2)} ms`")

#A test command to make sure the bot is handling arguments properly in the current context
@bot.command()
async def echo(ctx, *, args):
    await ctx.send(args)

#If the debug flag is enabled log messages to console to ensure the bot is connected properly
@bot.event
async def on_message(message):
    if debug == True:
        print(f"{message.guild} - #{message.channel} - {message.author}({message.author.id}): {message.content}")
    await bot.process_commands(message)

bot.run(settings['bot-token'])