from datetime import datetime, timezone

from config.settings import DANGEROUS_REGIMES


class MarketEngine:

    def __init__(self):
        self.market_regime = "UNKNOWN"
        self.sentiment = "NEUTRAL"
        self.volatility = 0
        self.last_update = None

    def update_market(self, regime, sentiment, volatility):
        self.market_regime = regime
        self.sentiment = sentiment
        self.volatility = volatility
        self.last_update = datetime.now(timezone.utc)

    def get_market_state(self):
        return {
            "market_regime": self.market_regime,
            "sentiment": self.sentiment,
            "volatility": self.volatility,
            "last_update": str(self.last_update),
        }

    def is_safe_market(self):
        return self.market_regime not in DANGEROUS_REGIMES


if __name__ == "__main__":
    market = MarketEngine()

    market.update_market(
        regime="BULL",
        sentiment="POSITIVE",
        volatility=15,
    )

    print(market.get_market_state())
