class PortfolioManager:

    def __init__(self):

        self.total_capital = 0
        self.allocated_capital = {}

    def allocate_capital(self, bot_name, amount):

        self.allocated_capital[bot_name] = amount

    def get_portfolio(self):

        return self.allocated_capital


if __name__ == "__main__":

    portfolio = PortfolioManager()

    portfolio.allocate_capital(
        "TrendBot",
        5000
    )

    portfolio.allocate_capital(
        "ScalperBot",
        3000
    )

    print(portfolio.get_portfolio())
