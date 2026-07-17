class DataFeed:
    """Market data source for the fleet.

    Currently a manual/static feed. Later this can be replaced with a
    live exchange API without changing the rest of the system, as long
    as get_snapshot() keeps the same shape.
    """

    def __init__(self):
        self.snapshot = {
            "regime": "UNKNOWN",
            "sentiment": "NEUTRAL",
            "volatility": 0,
            "market_drop": 0,
        }

    def set_snapshot(self, regime, sentiment, volatility, market_drop=0):
        self.snapshot = {
            "regime": regime,
            "sentiment": sentiment,
            "volatility": volatility,
            "market_drop": market_drop,
        }

    def get_snapshot(self):
        return self.snapshot


if __name__ == "__main__":
    feed = DataFeed()

    feed.set_snapshot(
        regime="BULL",
        sentiment="POSITIVE",
        volatility=15,
    )

    print(feed.get_snapshot())
