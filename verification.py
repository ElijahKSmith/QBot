import json
import requests
import sqlite3
import discord

import checks
import resolve_host

from discord.ext import commands
from pathlib import Path

class Verification(commands.Cog, name="Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(checks.is_unverified)
    @commands.guild_only()
    async def register(self, ctx, *, args):
        member = ctx.author.id

        settings = json.loads(list(Path('.').glob('config.json'))[0].read_text())
        host = resolve_host.switch_platform(settings['region'])

        #Check to see if the summoner that was passed in is real on the server in config
        parsed_summoner = requests.utils.quote(args)
        query = host + 'summoner/v4/summoners/by-name/' + parsed_summoner
        payload = {'api_key': settings['riot-api-key']}
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
        info = (member, summoner['name'])

        conn = sqlite3.connect('server.db')
        c = conn.cursor()
        c.execute("INSERT INTO unverified VALUES (?,?)", info)
        conn.commit()
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

    #TODO: Add error catch for if user has DMs from server turned off
    @register.error
    async def register_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"<@{ctx.author.id}> , you cannot register, you may be already registered or are currently in the verification process.")
        else:
            print(error)

def setup(bot):
    bot.add_cog(Verification(bot))

def teardown(bot):
    bot.remove_cog("Verification")