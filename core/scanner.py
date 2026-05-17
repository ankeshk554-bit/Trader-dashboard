import yfinance as yf
import pandas as pd
import ta


def clean_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def institutional_score(df):

    df = clean_columns(df)

    close = float(df["Close"].iloc[-1])

    ema50 = ta.trend.ema_indicator(df["Close"], window=50).iloc[-1]
    ema200 = ta.trend.ema_indicator(df["Close"], window=200).iloc[-1]

    rsi = ta.momentum.RSIIndicator(df["Close"]).rsi().iloc[-1]

    avg_volume = df["Volume"].rolling(20).mean().iloc[-1]
    current_volume = df["Volume"].iloc[-1]

    score = 0

    if close > ema50:
        score += 25

    if ema50 > ema200:
        score += 25

    if 55 < rsi < 75:
        score += 25

    if current_volume > avg_volume:
        score += 25

    return score


def scan_stock(symbol):

    try:

        df = yf.download(
            symbol,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df = clean_columns(df)

        score = institutional_score(df)

        close = float(df["Close"].iloc[-1])

        ema50 = ta.trend.ema_indicator(df["Close"], window=50).iloc[-1]

        signal = "NEUTRAL"

        if close > ema50 and score >= 75:
            signal = "BUY"

        elif close < ema50 and score <= 25:
            signal = "SELL"

        return {
            "Symbol": symbol,
            "Close": round(close, 2),
            "Score": score,
            "Signal": signal
        }

    except:
        return None