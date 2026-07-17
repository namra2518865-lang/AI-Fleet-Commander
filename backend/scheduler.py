from datetime import datetime


class Scheduler:

    def __init__(self):

        self.last_market_scan = None

        self.last_ranking_update = None

        self.last_capital_rotation = None

        self.last_portfolio_audit = None

    def market_scan(self):

        self.last_market_scan = datetime.now()

        print(

            "[SCAN]",

            self.last_market_scan

        )

    def ranking_update(self):

        self.last_ranking_update = datetime.now()

        print(

            "[RANKING]",

            self.last_ranking_update

        )

    def capital_rotation(self):

        self.last_capital_rotation = datetime.now()

        print(

            "[CAPITAL]",

            self.last_capital_rotation

        )

    def portfolio_audit(self):

        self.last_portfolio_audit = datetime.now()

        print(

            "[AUDIT]",

            self.last_portfolio_audit

        )


if __name__ == "__main__":

    scheduler = Scheduler()

    scheduler.market_scan()

    scheduler.ranking_update()

    scheduler.capital_rotation()

    scheduler.portfolio_audit()