"""Central configuration for AI Fleet Commander.

All engines read shared values from here instead of hardcoding them.
"""

# Market regimes that force the fleet into defensive mode
DANGEROUS_REGIMES = [
    "FLASH_CRASH",
    "BLACK_SWAN",
    "EXTREME_VOLATILITY",
]

# Risk settings (percentages)
MAX_RISK_PERCENT = 2
MAX_TRADE_SIZE_PERCENT = 10
STOP_LOSS_PERCENT = 3

# Kill switch thresholds
KILL_SWITCH_PORTFOLIO_RISK = 8
KILL_SWITCH_MARKET_DROP = 4

# Capital
TOTAL_CAPITAL = 10000

# Volatility level above which DefenseBot activates
DEFENSE_VOLATILITY_THRESHOLD = 30

# Default opportunity-score weights used for any bot
# that has no specific entry in BOT_WEIGHTS.
DEFAULT_BOT_WEIGHTS = {
    "setup": 0.30,
    "market_fit": 0.30,
    "risk_reward": 0.20,
    "confidence": 0.20,
}

# Per-bot opportunity-score weights (keys match bot class names)
BOT_WEIGHTS = {
    "TrendBot": {
        "setup": 0.30,
        "market_fit": 0.30,
        "risk_reward": 0.20,
        "confidence": 0.20,
    },
    "ScalperBot": {
        "setup": 0.40,
        "market_fit": 0.20,
        "risk_reward": 0.25,
        "confidence": 0.15,
    },
    "MomentumBot": {
        "setup": 0.35,
        "market_fit": 0.25,
        "risk_reward": 0.25,
        "confidence": 0.15,
    },
    "DefenseBot": {
        "setup": 0.20,
        "market_fit": 0.40,
        "risk_reward": 0.20,
        "confidence": 0.20,
    },
}
