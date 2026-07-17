class ScalperBot:

    def __init__(self):

        self.name = "ScalperBot"
        self.status = "IDLE"

    def analyze_market(self, market_regime):

        if market_regime == "SIDEWAYS":

            self.status = "SCALP"

        else:

            self.status = "WAIT"

    def get_status(self):

        return {
            "bot": self.name,
            "status": self.status
        }


if __name__ == "__main__":

    bot = ScalperBot()

    bot.analyze_market("SIDEWAYS")

    print(bot.get_status())