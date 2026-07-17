class BotRankingEngine:

    def calculate_score(

        self,

        profit_factor,

        drawdown,

        market_fit,

        opportunity

    ):

        score = (

            profit_factor * 30

            +

            (100 - drawdown) * 0.25

            +

            market_fit * 0.25

            +

            opportunity * 0.20

        )

        return round(

            score,

            2

        )


if __name__ == "__main__":

    ranking = BotRankingEngine()

    score = ranking.calculate_score(

        profit_factor=2.8,

        drawdown=5.6,

        market_fit=95,

        opportunity=90

    )

    print(

        "BOT SCORE:",

        score

    )