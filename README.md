# Stock Trading Signal App

A desktop application built with Python and tkinter that uses the Simple Moving Average (SMA) Crossover strategy to generate Buy / Sell / Hold signals for any stock ticker.

It uses real stock data from Yahoo Finance through the `yfinance` library, so no API key is necessary.

## Strategy

This app uses the Simple Moving Average (SMA) Crossover strategy.

- **BUY / HOLD LONG**: Short SMA crosses above Long SMA, which suggests bullish momentum.
- **SELL / STAY OUT**: Short SMA crosses below Long SMA, which suggests bearish momentum.
- **NEUTRAL**: Short SMA and Long SMA are equal, meaning there is no clear signal.

Default settings:

- 20-day short SMA
- 50-day long SMA

## Requirements

- Python 3.10+
- Libraries listed in `requirements.txt`
