from config.settings import (
    MAX_RISK_PERCENT,
    MAX_TRADE_SIZE_PERCENT,
    STOP_LOSS_PERCENT,
)


class RiskEngine:

    def __init__(self):
        self.max_risk = MAX_RISK_PERCENT
        self.max_trade_size = MAX_TRADE_SIZE_PERCENT
        self.stop_loss = STOP_LOSS_PERCENT

    def calculate_risk(self, capital):
        trade_size = capital * (self.max_trade_size / 100)
        risk_amount = trade_size * (self.max_risk / 100)

        return {
            "capital": capital,
            "trade_size": trade_size,
            "risk_amount": risk_amount,
            "stop_loss": self.stop_loss,
        }


if __name__ == "__main__":
    risk = RiskEngine()

    print(risk.calculate_risk(10000))
