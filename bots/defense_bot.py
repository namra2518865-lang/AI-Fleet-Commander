class DefenseBot:

    def __init__(self):

        self.name = "DefenseBot"
        self.status = "IDLE"

    def analyze_risk(self, volatility):

        if volatility > 30:

            self.status = "DEFEND"

        else:

            self.status = "NORMAL"

    def get_status(self):

        return {
            "bot": self.name,
            "status": self.status
        }


if __name__ == "__main__":

    bot = DefenseBot()

    bot.analyze_risk(40)

    print(bot.get_status())