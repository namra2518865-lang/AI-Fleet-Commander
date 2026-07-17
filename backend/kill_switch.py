from config.settings import (
    KILL_SWITCH_MARKET_DROP,
    KILL_SWITCH_PORTFOLIO_RISK,
)


class KillSwitch:

    def __init__(self):
        self.active = False

    def evaluate(self, portfolio_risk, market_drop):
        if portfolio_risk >= KILL_SWITCH_PORTFOLIO_RISK:
            self.active = True

        if market_drop >= KILL_SWITCH_MARKET_DROP:
            self.active = True

        return self.active

    def reset(self):
        self.active = False


if __name__ == "__main__":
    kill = KillSwitch()

    print(kill.evaluate(portfolio_risk=9, market_drop=5))
