# 📈 Crypto Swing Trading Bot

This project is a **crypto trading bot** designed to perform **swing trading** on the Binance exchange using Python. It is built with modular architecture, including adapters, application services, and domain logic, and leverages Redis for state caching and Telegram for real-time notifications.

---

## 💡 What is Swing Trading?

**Swing trading** is a trading strategy that aims to capture short- to medium-term gains in a financial instrument over a period of a few days to several weeks. Traders use technical analysis to look for opportunities where assets experience price "swings" — periods of upward or downward momentum — to enter or exit positions.

This bot uses swing trading techniques to respond to **market volatility**, with the goal of making profitable trades during price spikes or dips.

---

## 🎯 Goal

The primary goal of this bot is to **maximize the total USD value** held in the Binance account over time.

The approach:
- Start with a balance in a base asset (e.g. ETH).
- Monitor market conditions in real time.
- Use trading signals to buy or sell assets, always aiming to **increase the USD-equivalent value** of the holdings.

---

## 📊 Trading Indicators Used

This bot uses a combination of key technical indicators:

### 1. Relative Strength Index (RSI)
- A momentum oscillator that measures the speed and change of price movements.
- Values range from 0 to 100.
- Typically:
  - RSI > 70 → **Overbought** (potential sell signal)
  - RSI < 30 → **Oversold** (potential buy signal)

### 2. Exponential Moving Average (EMA)
- A moving average that gives more weight to recent price data.
- Helps identify trends and dynamic support/resistance levels.
- Commonly used to determine if the market is trending up or down.

These indicators are combined to make smarter, conservative trading decisions that react to market momentum and reversals.

---

## 🧱 Tech Stack

- **Python 3.13**
- **Pipenv** for dependency management
- **Redis** for caching trading state and balances
- **Binance API** for placing trades and getting real-time data
- **Telegram Bot** for alerting trade actions and system updates