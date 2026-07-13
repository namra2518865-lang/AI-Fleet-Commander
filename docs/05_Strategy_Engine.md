# AI Fleet Commander
# Strategy Engine

Version: 1.0

---

# Purpose

The Strategy Engine is responsible for evaluating, ranking, activating, and allocating capital across all trading strategies.

Unlike individual trading bots, the Strategy Engine operates at the portfolio level.

Its goal is to ensure that capital is always assigned to the most suitable strategy based on current market conditions.

---

# Responsibilities

The Strategy Engine continuously:

- Evaluates every strategy
- Calculates confidence scores
- Detects market compatibility
- Ranks all strategies
- Approves strategy activation
- Pauses weak strategies
- Sends recommendations to the Capital Engine

---

# Strategy Lifecycle

Every strategy exists in one of the following states:

ACTIVE

READY

WATCHLIST

PAUSED

DISABLED

---

# Evaluation Factors

Each strategy receives a score based on:

- Market Regime Fit
- Trend Alignment
- Volatility Compatibility
- Liquidity Conditions
- Recent Performance
- Win Rate
- Drawdown
- Risk Score
- Opportunity Quality
- Portfolio Exposure

---

# Confidence Score

Each strategy receives a confidence score between 0 and 100.

0–20

Very Weak

21–40

Weak

41–60

Neutral

61–80

Strong

81–100

Excellent

---

# Dynamic Ranking

Strategies are ranked continuously.

The highest-ranked strategy receives the highest priority for capital allocation.

Ranking changes whenever market conditions change.

---

# Capital Competition

Strategies compete for capital.

Capital is never assigned permanently.

Every strategy must continuously earn its allocation.

---

# Activation Rules

A strategy may become ACTIVE only if:

- Market regime matches
- Confidence > 70
- Portfolio risk acceptable
- No conflicting exposure
- Opportunity quality sufficient

---

# Pause Rules

A strategy is paused when:

- Confidence falls below threshold
- Drawdown exceeds limit
- Market regime changes
- Risk becomes excessive

---

# Strategy Switching

The Strategy Engine may switch strategies whenever:

- Market regime changes
- Better opportunity appears
- Confidence ranking changes

Switching should be controlled to avoid unnecessary churn.

---

# Communication

The Strategy Engine sends data to:

- Bot Ranking Engine
- Capital Engine
- Portfolio Manager
- Risk Engine

---

# Goal

The Strategy Engine ensures that the right strategy receives capital at the right time while maintaining portfolio stability and long-term consistency.
