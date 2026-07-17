from config.settings import BOT_WEIGHTS, DEFAULT_BOT_WEIGHTS


class OpportunityEngine:

    def __init__(self):
        self.bot_scores = {}

    def calculate_opportunity(
        self,
        bot_name,
        setup_quality,
        market_fit,
        risk_reward,
        confidence,
    ):
        weights = BOT_WEIGHTS.get(bot_name, DEFAULT_BOT_WEIGHTS)

        score = (
            setup_quality * weights["setup"]
            + market_fit * weights["market_fit"]
            + risk_reward * weights["risk_reward"]
            + confidence * weights["confidence"]
        )

        self.bot_scores[bot_name] = round(score, 2)

        return self.bot_scores[bot_name]

    def rank_bots(self):
        return sorted(
            self.bot_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )


if __name__ == "__main__":
    engine = OpportunityEngine()

    engine.calculate_opportunity(
        "ScalperBot",
        setup_quality=95,
        market_fit=90,
        risk_reward=85,
        confidence=92,
    )

    engine.calculate_opportunity(
        "TrendBot",
        setup_quality=82,
        market_fit=80,
        risk_reward=78,
        confidence=84,
    )

    print(engine.rank_bots())
