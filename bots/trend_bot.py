class TrendBot:

    def __init__(self):

        self.name = "TrendBot"
        self.status = "IDLE"

    def analyze_market(self, market_regime):

        if market_regime == "BULL":

            self.status = "BUY"

        elif market_regime == "BEAR":

            self.status = "SELL"

        else:

            self.status = "WAIT"

    def get_status(self):

        return {
            "bot": self.name,
            "status": self.status
        }


if __name__ == "__main__":

    bot = TrendBot()

    bot.analyze_market("BULL")

    print(bot.get_status())