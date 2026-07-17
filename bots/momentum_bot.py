class MomentumBot:

    def __init__(self):

        self.name = "MomentumBot"
        self.status = "IDLE"

    def analyze_market(self, sentiment):

        if sentiment == "POSITIVE":

            self.status = "BUY"

        elif sentiment == "NEGATIVE":

            self.status = "SELL"

        else:

            self.status = "WAIT"

    def get_status(self):

        return {
            "bot": self.name,
            "status": self.status
        }


if __name__ == "__main__":

    bot = MomentumBot()

    bot.analyze_market("POSITIVE")

    print(bot.get_status())