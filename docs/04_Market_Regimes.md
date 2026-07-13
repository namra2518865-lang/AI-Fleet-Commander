# AI Fleet Commander
# Market Regimes

Version: 1.0

---

# Purpose

The Market Regime Engine classifies the current market into predefined states.

Every strategy, every bot, and every capital allocation decision depends on the active market regime.

The Market Regime is the bridge between Market Brain and Strategy Engine.

---

# Golden Rule

One market.

One dominant regime.

One portfolio strategy.

The Fleet Commander must avoid conflicting decisions by selecting one primary market regime while allowing a secondary regime only when confidence is low.

---

# Supported Market Regimes

The Fleet Commander recognizes the following primary regimes:

1. Strong Bull Trend
2. Bull Trend
3. Sideways Range
4. High Volatility Range
5. Breakout
6. Breakdown
7. Weak Bear
8. Strong Bear
9. Recovery
10. Capitulation

---

# Strong Bull Trend

Characteristics

- Higher Highs
- Higher Lows
- Strong Momentum
- High Volume
- Positive Funding
- Strong Market Structure

Preferred Strategies

- Trend Following
- Trend Pullback
- SuperTrend
- Breakout

Preferred Bots

- Bot 2
- Bot 4
- Bot 8
- Bot 10
- Bot 11

Avoid

- Grid
- Mean Reversion

Risk Level

LOW

Capital Usage

80–100%

---

# Bull Trend

Characteristics

- Healthy Uptrend
- Moderate Pullbacks
- Stable Volume

Preferred Bots

- Bot 2
- Bot 4
- Bot 10

Capital Usage

70–90%

---

# Sideways Range

Characteristics

- Flat Market
- Low Momentum
- Oscillation
- Repeated Support & Resistance

Preferred Bots

- Bot 1
- Bot 5
- Bot 7

Avoid

- Trend Strategies

Capital Usage

40–70%

---

# High Volatility Range

Characteristics

- Wide Swings
- Fake Breakouts
- Fast Reversals

Preferred Bots

- Bot 1
- Bot 5
- Bot 9

Reduce Position Size

YES

---

# Breakout

Characteristics

- Volume Expansion
- Volatility Expansion
- Structure Break
- Momentum Confirmation

Preferred Bots

- Bot 6
- Bot 8
- Bot 11

Capital Usage

80%

---

# Breakdown

Characteristics

- Major Support Break
- High Selling Pressure

Preferred Bots

- Short Trend Bots
- Futures Trend Bots

Spot Allocation

Reduced

---

# Weak Bear

Characteristics

- Lower Highs
- Weak Momentum

Preferred Bots

- Defensive Trend
- Small Position Sizes

Capital Usage

40%

---

# Strong Bear

Characteristics

- Heavy Selling
- Panic
- High Liquidations

Preferred Bots

- Defensive Futures
- Contrarian Monitoring

Spot Exposure

Minimum

---

# Recovery

Characteristics

- Selling Exhaustion
- Higher Lows
- Improving Volume

Preferred Bots

- Bot 9
- Bot 7
- Bot 4

Capital Usage

60%

---

# Capitulation

Characteristics

- Panic Selling
- Fear Extreme
- Liquidation Cascade

Preferred Bots

- Bot 7
- Bot 9

Aggressive Buying

NO

Scale In Only

YES

---

# Dynamic Regime Switching

The Fleet Commander continuously monitors the market.

Whenever confidence in the current regime drops below the required threshold, the Market Brain performs a full reclassification.

A regime change automatically triggers:

- Strategy Re-ranking
- Bot Re-ranking
- Capital Reallocation
- Risk Reassessment
- Opportunity Re-evaluation

---

# Regime Confidence

Every detected regime receives a confidence score.

0–40 → Weak

41–60 → Moderate

61–80 → Strong

81–100 → Very Strong

Capital allocation depends on confidence.

---

# Spot vs Futures

Every regime independently evaluates:

Spot

Futures

The preferred market can differ depending on the regime.

---

# Communication

The Market Regime Engine sends the active regime to:

- Strategy Engine
- Bot Ranking Engine
- Capital Engine
- Risk Engine
- Portfolio Manager

No module may ignore the active market regime.

---

# Conclusion

The Market Regime Engine converts raw market data into actionable portfolio intelligence.

It ensures that every strategy operates only in the market conditions where it has the highest probability of success.
