class BotManager:
    """Keeps track of all bot instances in the fleet."""

    def __init__(self):
        self.bots = {}

    def register_bot(self, bot):
        self.bots[bot.name] = bot

    def get_bot(self, bot_name):
        return self.bots.get(bot_name)

    def get_all_statuses(self):
        return [bot.get_status() for bot in self.bots.values()]

    def bot_names(self):
        return list(self.bots.keys())


if __name__ == "__main__":
    from bots.trend_bot import TrendBot

    manager = BotManager()
    manager.register_bot(TrendBot())

    print(manager.get_all_statuses())
