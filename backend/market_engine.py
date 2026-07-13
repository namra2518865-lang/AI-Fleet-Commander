from datetime import datetime


class MarketEngine:

    def __init__(self):

        self.market_regime = "UNKNOWN"

        self.sentiment = "NEUTRAL"

        self.volatility = 0

        self.last_update = None

    def update_market(
        self,
        regime,
        sentiment,
        volatility
    ):

        self.market_regime = regime

        self.sentiment = sentiment

        self.volatility = volatility

        self.last_update = datetime.utcnow()

    def get_market_state(self):

        return {

            "market_regime": self.market_regime,

            "sentiment": self.sentiment,

            "volatility": self.volatility,

            "last_update": str(self.last_update)

        }

    def is_safe_market(self):

        dangerous_regimes = [

            "FLASH_CRASH",

            "BLACK_SWAN",

            "EXTREME_VOLATILITY"

        ]

        return self.market_regime not in dangerous_regimes
