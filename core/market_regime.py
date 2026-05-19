import yfinance as yf
import pandas as pd
import ta


def clean_columns(df):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def get_market_regime():

    try:

        df = yf.download(
            "^NSEI",
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return "UNKNOWN"

        df = clean_columns(df)

        close = float(df["Close"].iloc[-1])

        ema50 = ta.trend.ema_indicator(
            df["Close"],
            window=50
        ).iloc[-1]

        ema200 = ta.trend.ema_indicator(
            df["Close"],
            window=200
        ).iloc[-1]

        if close > ema50 > ema200:
            return "BULLISH"

        elif close < ema50 < ema200:
            return "BEARISH"

        else:
            return "SIDEWAYS"

    except Exception as e:

        print(f"Market Regime Error: {e}")

        return "UNKNOWN"