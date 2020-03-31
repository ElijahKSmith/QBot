import sqlite3

conn = sqlite3.connect('server.db')

conn.execute('''CREATE TABLE verified(
             discordId  TEXT PRIMARY KEY NOT NULL,
             summoner   TEXT             NOT NULL,
             summonerId TEXT             NOT NULL,
             accountId  TEXT             NOT NULL,
             puuid      TEXT             NOT NULL,
             role       TEXT             NOT NULL
             );''')

conn.execute('''CREATE TABLE unverified(
             discordId TEXT PRIMARY KEY NOT NULL,
             summoner  TEXT             NOT NULL
             );''')

conn.close()