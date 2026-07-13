# AI Fleet Commander
# Bot Ranking Engine

Version: 1.0

---

# Purpose

The Bot Ranking Engine is responsible for continuously evaluating all trading bots and determining which bots deserve portfolio capital.

Ranking is dynamic.

It changes every time market conditions change.

No bot has permanent priority.

---

# Philosophy

Bots do not receive capital because of their identity.

Bots receive capital because they currently have the highest probability of success.

Every bot competes equally.

---

# Evaluation Frequency

The Bot Ranking Engine runs continuously.

Default:

Every 60 seconds

If high volatility:

Every 15 seconds

If emergency:

Immediately

---

# Bot Score

Each bot receives a Dynamic Score.

Range

0 — 100

Higher score

Higher priority

---

# Score Components

Market Fit

30%

Confidence

20%

Recent Performance

10%

Win Rate

10%

Profit Factor

10%

Drawdown

-10%

Risk Score

-5%

Opportunity Quality

15%

Total

100%

---

# Market Fit

Questions

Does this strategy match the current market?

Example

Grid

Excellent

Sideways

Poor

Strong Bull

Trend Pullback

Excellent

Bull Market

Poor

Range

---

# Confidence

Calculated from:

Signal Quality

Indicator Agreement

Multi Timeframe Alignment

Volume Confirmation

Momentum

News Filter

---

# Recent Performance

Evaluate

Last 10 trades

Last 30 trades

Last 7 days

Performance receives higher weight than older history.

---

# Win Rate

Measure

Winning %

Do not rely only on win rate.

Combine with Profit Factor.

---

# Profit Factor

Gross Profit

/

Gross Loss

Higher Profit Factor

Higher Score

---

# Drawdown Penalty

Drawdown reduces ranking.

Example

Drawdown

2%

Penalty

Low

Drawdown

12%

Penalty

High

---

# Risk Score

Risk includes

Leverage

Exposure

Volatility

Liquidation Risk

Correlation

Higher risk

Lower score

---

# Opportunity Quality

Evaluate

Risk Reward

Trend

Liquidity

Momentum

Support

Resistance

Market Structure

News

Funding

Open Interest

---

# Ranking Levels

90-100

Elite

80-89

Excellent

70-79

Strong

60-69

Good

50-59

Average

Below 50

Low Priority

---

# Capital Priority

Top Ranked

Highest Allocation

Second

Medium Allocation

Third

Reduced Allocation

Bottom

No Capital

---

# Dynamic Re-ranking

Every market update triggers:

Recalculate Scores

↓

Update Rankings

↓

Update Capital

↓

Notify Portfolio Manager

---

# Tie Break Rules

If two bots have equal scores:

Higher Confidence Wins

↓

Higher Market Fit Wins

↓

Lower Drawdown Wins

↓

Higher Profit Factor Wins

↓

Lower Risk Wins

---

# AI Advisor

Bot 11 reviews all rankings.

Bot 11 may suggest:

Increase Allocation

Reduce Allocation

Pause Strategy

Resume Strategy

Rotate Capital

Suggestions only.

No authority.

---

# Emergency Override

Immediately reduce ranking if:

Flash Crash

Exchange Failure

Extreme Funding

Extreme Liquidations

Major News

Portfolio Emergency

---

# Final Rule

Every bot starts equal.

Every minute,

they must earn their position again.

Ranking never becomes permanent.

---

# Conclusion

The Bot Ranking Engine is the competitive intelligence layer of AI Fleet Commander.

It ensures that capital is continuously redirected toward the strongest opportunities while protecting the portfolio from weak or deteriorating strategies.
