class StrategyEngine:

    def __init__(self):

        self.active_bots = []

    def register_bot(self, bot_name):

        self.active_bots.append(bot_name)

    def get_active_bots(self):

        return self.active_bots
