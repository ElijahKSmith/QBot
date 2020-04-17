import sqlite3
from discord.ext import commands

#Checks to see if a user entry for the user in context exists in the verified table
async def is_verified(ctx):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    member = (str(ctx.author.id),)

    cursor.execute("SELECT discordId FROM verified WHERE discordId=?", member)
    result = cursor.fetchone()
    conn.close()

    return result != None

#Checks to see if a user entry for the user in context exists in the unverified table
async def pending_verification(ctx):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    member = (str(ctx.author.id),)

    cursor.execute("SELECT discordId FROM unverified WHERE discordId=?", member)
    result = cursor.fetchone()
    conn.close()

    return result != None

#Checks to see if a user entry for the user in context does not exist in either the verified or unverified table
async def is_unverified(ctx):
    conn = sqlite3.connect('server.db')
    cursor = conn.cursor()
    member = (str(ctx.author.id),)

    cursor.execute("SELECT discordId FROM verified WHERE discordId=?", member)
    result = cursor.fetchone()

    if result != None:
        conn.close()
        return False
    else:
        cursor.execute("SELECT discordId FROM unverified WHERE discordId=?", member)
        result = cursor.fetchone()
        conn.close()

        return result == None
