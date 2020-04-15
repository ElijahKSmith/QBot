class Player:
    def __init__(self, discordId, summoner, rank, role=None):
        self.discordId = discordId
        self.summoner = summoner
        self.rank = rank
        self.role = role