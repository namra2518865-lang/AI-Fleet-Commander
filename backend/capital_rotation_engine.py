class CapitalRotationEngine:

    def __init__(self, total_capital):
        self.total_capital = total_capital

    def allocate_capital(self, ranked_bots):
        """Split total capital across bots in proportion to their scores.

        ranked_bots is a list of (bot_name, score) tuples.
        """
        total_score = sum(score for _, score in ranked_bots)

        if total_score == 0:
            return {bot_name: 0 for bot_name, _ in ranked_bots}

        allocations = {}

        for bot_name, score in ranked_bots:
            capital = (score / total_score) * self.total_capital
            allocations[bot_name] = round(capital, 2)

        return allocations


if __name__ == "__main__":
    engine = CapitalRotationEngine(total_capital=1200)

    ranked_bots = [
        ("ScalperBot", 91.15),
        ("TrendBot", 81.10),
        ("MomentumBot", 88.40),
        ("DefenseBot", 84.70),
    ]

    print(engine.allocate_capital(ranked_bots))
